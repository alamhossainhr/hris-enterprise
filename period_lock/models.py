from django.db import models
from core.models import TimeStampedModel
from organization.models import Company

class PeriodLockMaster(TimeStampedModel):
    LockKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='CompanyKey')
    Year = models.IntegerField()
    Month = models.IntegerField()
    IsAttendanceLocked = models.BooleanField(default=False)
    IsLeaveLocked = models.BooleanField(default=False)
    IsOTLocked = models.BooleanField(default=False)
    IsPayrollLocked = models.BooleanField(default=False)
    LockedAt = models.DateTimeField(null=True, blank=True)
    LockedBy = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = 'PeriodLockMaster'
        unique_together = (('Company', 'Year', 'Month'),)
