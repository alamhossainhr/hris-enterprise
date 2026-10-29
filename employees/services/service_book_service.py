from datetime import date
from django.db import transaction
from employees.models import DigitalServiceBook
from audit.models import SystemAuditTrail

class ServiceBookService:
    @classmethod
    @transaction.atomic
    def record_event(cls, emp_key: int, event_type: str, effective_date: date, **kwargs) -> DigitalServiceBook:
        entry = DigitalServiceBook.objects.create(
            EmpKey=emp_key,
            EventType=event_type,
            EffectiveDate=effective_date,
            PreviousCompanyID=kwargs.get("prev_company"),
            NewCompanyID=kwargs.get("new_company"),
            PreviousDepartmentID=kwargs.get("prev_dept"),
            NewDepartmentID=kwargs.get("new_dept"),
            PreviousDesignationID=kwargs.get("prev_desig"),
            NewDesignationID=kwargs.get("new_desig"),
            PreviousSalary=kwargs.get("prev_salary"),
            NewSalary=kwargs.get("new_salary"),
            Remarks=kwargs.get("remarks"),
            ApprovedBy=kwargs.get("approved_by"),
            created_by=kwargs.get("user", "SYSTEM"),
        )
        SystemAuditTrail.objects.create(
            EmpKey=emp_key,
            ModuleName="DigitalServiceBook",
            Action=f"EVENT_{event_type}",
            TableName="DigitalServiceBook",
            RecordKey=str(entry.EventKey),
            Reason=kwargs.get("remarks", "Service history milestone updated"),
            Username=kwargs.get("user", "SYSTEM"),
        )
        return entry
