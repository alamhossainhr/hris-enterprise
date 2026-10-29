from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES = {
    # 1. LEAVE MODELS
    "leave/models.py": '''from django.db import models
from core.models import TimeStampedModel
from organization.models import Company

class LeaveTypeMaster(TimeStampedModel):
    LeaveTypeKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column="CompanyKey")
    TypeCode = models.CharField(max_length=20)  # CL, SL, EL, ML, CPL, LWP
    TypeName = models.CharField(max_length=100)
    YearlyEntitlement = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    IsPaid = models.BooleanField(default=True)
    IsEarned = models.BooleanField(default=False)
    AllowCarryForward = models.BooleanField(default=False)
    MaxCarryForwardDays = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    AllowEncashment = models.BooleanField(default=False)
    ApplicableGender = models.CharField(max_length=20, default="ALL")  # ALL, MALE, FEMALE
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = "LeaveTypeMaster"
        unique_together = (("Company", "TypeCode"),)

    def __str__(self):
        return f"{self.TypeName} ({self.TypeCode})"

class LeaveBalance(TimeStampedModel):
    BalanceKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    LeaveType = models.ForeignKey(LeaveTypeMaster, on_delete=models.PROTECT, db_column="LeaveTypeKey")
    LeaveYear = models.IntegerField(db_index=True)
    OpeningBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    EarnedBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    AvailedBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    AdjustedBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    EncashedBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    ClosingBalance = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    class Meta:
        db_table = "LeaveBalance"
        unique_together = (("EmpKey", "LeaveType", "LeaveYear"),)

class LeaveApplication(TimeStampedModel):
    ApplicationKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    LeaveType = models.ForeignKey(LeaveTypeMaster, on_delete=models.PROTECT, db_column="LeaveTypeKey")
    FromDate = models.DateField()
    ToDate = models.DateField()
    TotalDays = models.DecimalField(max_digits=5, decimal_places=2)
    Reason = models.TextField()
    Status = models.CharField(max_length=30, default="PENDING")  # PENDING, APPROVED, REJECTED, CANCELLED
    ApprovedBy = models.CharField(max_length=100, null=True, blank=True)
    ApprovalDate = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "LeaveApplication"
        ordering = ["-FromDate"]

class MaternityBenefitRecord(TimeStampedModel):
    MaternityKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    EDD = models.DateField(help_text="Expected Delivery Date")
    LeaveStartDate = models.DateField()
    LeaveEndDate = models.DateField()
    AverageDailyWage = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    TotalBenefitAmount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    FirstInstallmentAmount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    FirstInstallmentPaidDate = models.DateField(null=True, blank=True)
    SecondInstallmentAmount = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    SecondInstallmentPaidDate = models.DateField(null=True, blank=True)
    IsApproved = models.BooleanField(default=False)

    class Meta:
        db_table = "MaternityBenefitRecord"
''',

    # 2. LEAVE SERVICES (Earn Leave Engine, Balance & Maternity)
    "leave/services/__init__.py": "",
    "leave/services/earn_leave_service.py": '''import datetime
from django.db import connection, transaction
from employees.models import EmployeeInfoDetails
from leave.models import LeaveTypeMaster, LeaveBalance
from attendance.services.table_service import AttendanceTableService

class EarnLeaveEngine:
    @classmethod
    @transaction.atomic
    def compute_yearly_earn_leave(cls, year: int, company_id: int = None, divisor: int = 18) -> dict:
        """
        Dynamically scans 12 monthly physical tables ([YYYY1]..[YYYY12]) in MSSQL,
        counts eligible present days, and credits EL to LeaveBalance.
        Formula: Earned = floor(Eligible Attendance Days / divisor)
        """
        emp_qs = EmployeeInfoDetails.objects.filter(IsActive=True)
        if company_id:
            emp_qs = emp_qs.filter(CompanyID=company_id)

        processed = 0
        credited_total = 0.0

        for emp in emp_qs:
            total_eligible_days = 0
            for month in range(1, 13):
                table_name = f"{year}{month}"
                if not AttendanceTableService.table_exists(table_name):
                    continue

                with connection.cursor() as cursor:
                    cursor.execute(f"""
                        SELECT COUNT(*) FROM [{table_name}] WITH (NOLOCK)
                        WHERE EmpKey = %s AND DayStatus IN ('P', 'PW', 'PH', 'L')
                    """, [emp.EmpKey])
                    total_eligible_days += cursor.fetchone()[0]

            earned_days = total_eligible_days // divisor
            if earned_days > 0:
                el_type = LeaveTypeMaster.objects.filter(TypeCode="EL").first()
                if el_type:
                    balance, _ = LeaveBalance.objects.get_or_create(
                        EmpKey=emp.EmpKey,
                        LeaveType=el_type,
                        LeaveYear=year,
                        defaults={"OpeningBalance": 0.0, "ClosingBalance": 0.0}
                    )
                    balance.EarnedBalance = earned_days
                    balance.ClosingBalance = (balance.OpeningBalance + balance.EarnedBalance + balance.AdjustedBalance) - (balance.AvailedBalance + balance.EncashedBalance)
                    balance.save()
                    credited_total += earned_days
                    processed += 1

        return {"status": "SUCCESS", "year": year, "employees_computed": processed, "total_el_credited": credited_total}
''',

    "leave/services/leave_service.py": '''from datetime import date
from django.db import transaction
from leave.models import LeaveTypeMaster, LeaveBalance, LeaveApplication
from core.exceptions import BusinessLogicError

class LeaveService:
    @classmethod
    @transaction.atomic
    def apply_leave(cls, emp_key: int, leave_type_id: int, from_date: date, to_date: date, reason: str) -> LeaveApplication:
        if from_date > to_date:
            raise BusinessLogicError("From Date cannot be later than To Date.")

        total_days = (to_date - from_date).days + 1
        leave_type = LeaveTypeMaster.objects.get(pk=leave_type_id)
        current_year = from_date.year

        balance, _ = LeaveBalance.objects.get_or_create(
            EmpKey=emp_key,
            LeaveType=leave_type,
            LeaveYear=current_year,
            defaults={"OpeningBalance": leave_type.YearlyEntitlement, "ClosingBalance": leave_type.YearlyEntitlement}
        )

        if leave_type.IsPaid and balance.ClosingBalance < total_days:
            raise BusinessLogicError(f"Insufficient leave balance. Available: {balance.ClosingBalance} days, Requested: {total_days} days.")

        app = LeaveApplication.objects.create(
            EmpKey=emp_key,
            LeaveType=leave_type,
            FromDate=from_date,
            ToDate=to_date,
            TotalDays=total_days,
            Reason=reason,
            Status="APPROVED",  # Default auto-approved for test pipeline
            ApprovedBy="HR Manager"
        )

        # Deduct balance
        balance.AvailedBalance += total_days
        balance.ClosingBalance = (balance.OpeningBalance + balance.EarnedBalance + balance.AdjustedBalance) - (balance.AvailedBalance + balance.EncashedBalance)
        balance.save()

        return app
''',

    "leave/services/maternity_service.py": '''import datetime
from decimal import Decimal
from django.db import transaction
from employees.models import EmployeeInfoDetails
from leave.models import MaternityBenefitRecord

class MaternityCalculationService:
    @classmethod
    @transaction.atomic
    def calculate_benefit(cls, emp_key: int, edd: datetime.date, leave_start_date: datetime.date) -> MaternityBenefitRecord:
        """
        Bangladesh Labor Act (BLA) Maternity Benefit Standard:
        16 Weeks (112 Days) Paid Benefit.
        Average daily wage = Preceding 3 months Gross / 90 (or 78 working days).
        Split: 50% First Installment (before delivery), 50% Second Installment (post delivery).
        """
        emp = EmployeeInfoDetails.objects.get(EmpKey=emp_key)
        gross = emp.GrossSalary or Decimal("0.00")
        
        # 3 months average wage computation
        total_3_months = gross * Decimal("3.0")
        daily_wage = round(total_3_months / Decimal("78.0"), 2)
        total_benefit = round(daily_wage * Decimal("112.0"), 2)
        installment = round(total_benefit / Decimal("2.0"), 2)

        leave_end_date = leave_start_date + datetime.timedelta(days=112)

        record = MaternityBenefitRecord.objects.create(
            EmpKey=emp_key,
            EDD=edd,
            LeaveStartDate=leave_start_date,
            LeaveEndDate=leave_end_date,
            AverageDailyWage=daily_wage,
            TotalBenefitAmount=total_benefit,
            FirstInstallmentAmount=installment,
            SecondInstallmentAmount=installment,
            IsApproved=True
        )
        return record
''',

    # 3. FORMS & VIEWS
    "leave/forms.py": '''from django import forms
from leave.models import LeaveTypeMaster, LeaveApplication, MaternityBenefitRecord

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ["LeaveType", "FromDate", "ToDate", "Reason"]
        widgets = {
            "LeaveType": forms.Select(attrs={"class": "form-select"}),
            "FromDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "ToDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "Reason": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

class MaternityApplicationForm(forms.Form):
    EmpKey = forms.IntegerField(widget=forms.HiddenInput())
    EDD = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    LeaveStartDate = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
''',

    "leave/views.py": '''import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from leave.models import LeaveTypeMaster, LeaveBalance, LeaveApplication, MaternityBenefitRecord
from leave.forms import LeaveApplicationForm, MaternityApplicationForm
from leave.services.leave_service import LeaveService
from leave.services.earn_leave_service import EarnLeaveEngine
from leave.services.maternity_service import MaternityCalculationService
from employees.models import EmployeeInfoDetails

def leave_dashboard(request):
    applications = LeaveApplication.objects.select_related("LeaveType").order_by("-FromDate")[:20]
    balances = LeaveBalance.objects.select_related("LeaveType").order_by("-LeaveYear")[:20]
    leave_types = LeaveTypeMaster.objects.all()
    return render(request, "leave/dashboard.html", {
        "applications": applications,
        "balances": balances,
        "leave_types": leave_types
    })

def apply_leave(request):
    emp = EmployeeInfoDetails.objects.first()
    if request.method == "POST":
        form = LeaveApplicationForm(request.POST)
        if form.is_valid():
            try:
                data = form.cleaned_data
                LeaveService.apply_leave(
                    emp_key=emp.EmpKey if emp else 1,
                    leave_type_id=data["LeaveType"].pk,
                    from_date=data["FromDate"],
                    to_date=data["ToDate"],
                    reason=data["Reason"]
                )
                messages.success(request, "Leave applied and balance updated successfully.")
                return redirect("leave_dashboard")
            except Exception as e:
                messages.error(request, str(e))
    else:
        form = LeaveApplicationForm()
    return render(request, "leave/apply.html", {"form": form, "emp": emp})

def compute_earn_leave_view(request):
    if request.method == "POST":
        year = int(request.POST.get("year", datetime.date.today().year))
        res = EarnLeaveEngine.compute_yearly_earn_leave(year)
        messages.success(request, f"Earn Leave Processed for {year}. {res['employees_computed']} employees received total {res['total_el_credited']} EL days.")
        return redirect("leave_dashboard")
    return render(request, "leave/compute_el.html")

def maternity_benefit_list(request):
    records = MaternityBenefitRecord.objects.all().order_by("-LeaveStartDate")
    return render(request, "leave/maternity_list.html", {"records": records})
''',

    "leave/urls.py": '''from django.urls import path
from leave import views

urlpatterns = [
    path("", views.leave_dashboard, name="leave_dashboard"),
    path("apply/", views.apply_leave, name="apply_leave"),
    path("earn-leave/compute/", views.compute_earn_leave_view, name="compute_earn_leave"),
    path("maternity/", views.maternity_benefit_list, name="maternity_benefit_list"),
]
''',

    # 4. TEMPLATES
    "templates/leave/dashboard.html": '''{% extends "base/base.html" %}
{% block page_title %}Leave Management & Earn Leave Registers{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h5 class="fw-bold mb-0 text-dark"><i class="bi bi-calendar2-check-fill text-primary me-2"></i>Leave Control & Entitlement</h5>
    <div class="d-flex gap-2">
        <a href="{% url 'apply_leave' %}" class="btn btn-sm btn-primary"><i class="bi bi-plus-lg me-1"></i> Apply Leave</a>
        <a href="{% url 'compute_earn_leave' %}" class="btn btn-sm btn-outline-info"><i class="bi bi-cpu-fill me-1"></i> Compute Earn Leave</a>
        <a href="{% url 'maternity_benefit_list' %}" class="btn btn-sm btn-outline-secondary"><i class="bi bi-heart-pulse-fill me-1"></i> Maternity Benefits</a>
    </div>
</div>

<div class="row g-4 mb-4">
    <div class="col-md-4">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3"><h6 class="m-0 fw-bold">Leave Policy Types</h6></div>
            <div class="card-body p-0">
                <table class="table table-hover align-middle mb-0 small">
                    <thead class="table-light"><tr><th>Code</th><th>Name</th><th>Entitlement</th><th>Paid</th></tr></thead>
                    <tbody>
                        {% for lt in leave_types %}
                        <tr>
                            <td class="fw-bold">{{ lt.TypeCode }}</td>
                            <td>{{ lt.TypeName }}</td>
                            <td>{{ lt.YearlyEntitlement }} Days</td>
                            <td>{% if lt.IsPaid %}<span class="badge bg-success">Paid</span>{% else %}<span class="badge bg-danger">Unpaid</span>{% endif %}</td>
                        </tr>
                        {% empty %}
                        <tr><td colspan="4" class="text-center text-muted py-3">No leave policies seeded.</td></tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="col-md-8">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3"><h6 class="m-0 fw-bold">Employee Leave Balance Overview</h6></div>
            <div class="card-body p-0">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0 small">
                        <thead class="table-light"><tr><th>EmpKey</th><th>Type</th><th>Year</th><th>Opening</th><th>Earned</th><th>Availed</th><th>Closing</th></tr></thead>
                        <tbody>
                            {% for b in balances %}
                            <tr>
                                <td class="fw-bold">{{ b.EmpKey }}</td>
                                <td><span class="badge bg-info text-dark">{{ b.LeaveType.TypeCode }}</span></td>
                                <td>{{ b.LeaveYear }}</td>
                                <td>{{ b.OpeningBalance }}</td>
                                <td class="text-success fw-bold">+{{ b.EarnedBalance }}</td>
                                <td class="text-danger fw-bold">-{{ b.AvailedBalance }}</td>
                                <td class="fw-bold fs-6">{{ b.ClosingBalance }}</td>
                            </tr>
                            {% empty %}
                            <tr><td colspan="7" class="text-center text-muted py-3">No balance records generated.</td></tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    "templates/leave/apply.html": '''{% extends "base/base.html" %}
{% block page_title %}Submit Leave Application{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3"><h6 class="m-0 fw-bold text-dark"><i class="bi bi-calendar-plus text-primary me-2"></i>Apply for Leave</h6></div>
            <div class="card-body p-4">
                <form method="POST">
                    {% csrf_token %}
                    {{ form.as_p }}
                    <div class="d-flex justify-content-end gap-2 mt-4">
                        <a href="{% url 'leave_dashboard' %}" class="btn btn-outline-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary">Submit Application</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    "templates/leave/compute_el.html": '''{% extends "base/base.html" %}
{% block page_title %}Earn Leave Statutory Computation Engine{% endblock %}
{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow-sm border-0">
            <div class="card-header bg-white py-3"><h6 class="m-0 fw-bold"><i class="bi bi-cpu-fill text-primary me-2"></i>Run Earn Leave Computation Engine</h6></div>
            <div class="card-body p-4">
                <p class="text-muted small">The statutory engine queries all 12 dynamic MSSQL monthly attendance tables (<code>[YYYY1]</code> &rarr; <code>[YYYY12]</code>), counts eligible working days, and computes credit: <code>Earned = floor(Eligible Attendance Days / 18)</code>.</p>
                <form method="POST">
                    {% csrf_token %}
                    <div class="mb-4">
                        <label class="form-label small fw-semibold">Target Year</label>
                        <input type="number" name="year" class="form-control" value="2026" required>
                    </div>
                    <div class="d-flex justify-content-end gap-2">
                        <a href="{% url 'leave_dashboard' %}" class="btn btn-outline-secondary">Cancel</a>
                        <button type="submit" class="btn btn-primary"><i class="bi bi-play-circle me-1"></i> Compute & Credit EL</button>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
''',

    "templates/leave/maternity_list.html": '''{% extends "base/base.html" %}
{% block page_title %}Bangladesh RMG Maternity Benefit Vault{% endblock %}
{% block content %}
<div class="d-flex justify-content-between align-items-center mb-4">
    <h5 class="fw-bold mb-0 text-dark"><i class="bi bi-heart-pulse-fill text-danger me-2"></i>Maternity Benefit Ledger (112 Days / 2-Tier Split)</h5>
    <a href="{% url 'leave_dashboard' %}" class="btn btn-sm btn-outline-secondary">Back to Leaves</a>
</div>
<div class="card shadow-sm border-0">
    <div class="card-body p-0">
        <table class="table table-hover align-middle mb-0 small">
            <thead class="table-light">
                <tr><th>EmpKey</th><th>EDD</th><th>Leave Window (112D)</th><th>Daily Wage</th><th>Total Benefit</th><th>1st Installment (50%)</th><th>2nd Installment (50%)</th><th>Status</th></tr>
            </thead>
            <tbody>
                {% for m in records %}
                <tr>
                    <td class="fw-bold">{{ m.EmpKey }}</td>
                    <td>{{ m.EDD }}</td>
                    <td>{{ m.LeaveStartDate }} &rarr; {{ m.LeaveEndDate }}</td>
                    <td>BDT {{ m.AverageDailyWage }}</td>
                    <td class="fw-bold text-primary">BDT {{ m.TotalBenefitAmount }}</td>
                    <td>BDT {{ m.FirstInstallmentAmount }}</td>
                    <td>BDT {{ m.SecondInstallmentAmount }}</td>
                    <td><span class="badge bg-success">Approved</span></td>
                </tr>
                {% empty %}
                <tr><td colspan="8" class="text-center text-muted py-4">No maternity benefit disbursements recorded.</td></tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endblock %}
''',

    # 5. ROUTING
    "config/urls.py": '''from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("organization/", include("organization.urls")),
    path("employees/", include("employees.urls")),
    path("shifts/", include("shifts.urls")),
    path("attendance/", include("attendance.urls")),
    path("leave/", include("leave.urls")),
    path("audit/", include("audit.urls")),
    path("api/v1/", include("api.v1.urls")),
]
''',
}

for filepath, content in FILES.items():
    p = BASE_DIR / filepath
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    print(f"Generated Phase 4 File: {filepath}")

print("\\n>>> PHASE 4 LEAVE, EARN LEAVE & MATERNITY MODULES COMPLETE <<<")