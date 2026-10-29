from django.db import models
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
