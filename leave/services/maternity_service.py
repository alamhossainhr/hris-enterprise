import datetime
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
