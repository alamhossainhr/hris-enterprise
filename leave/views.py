import datetime
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
