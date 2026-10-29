import datetime
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
