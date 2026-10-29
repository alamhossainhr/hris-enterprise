from django.db import models
from core.models import TimeStampedModel
from organization.models import Company

class ShiftMaster(TimeStampedModel):
    ShiftKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='CompanyKey')
    ShiftCode = models.CharField(max_length=30)
    ShiftName = models.CharField(max_length=100)
    StartTime = models.TimeField()
    EndTime = models.TimeField()
    GraceInMinutes = models.IntegerField(default=15)
    LateThresholdMinutes = models.IntegerField(default=30)
    EarlyExitThresholdMinutes = models.IntegerField(default=15)
    BreakMinutes = models.IntegerField(default=60)
    OTStartMinutesAfterShift = models.IntegerField(default=15)
    IsCrossMidnight = models.BooleanField(default=False)
    IsActive = models.BooleanField(default=True)

    class Meta:
        db_table = 'ShiftMaster'
        unique_together = (('Company', 'ShiftCode'),)

    def __str__(self):
        return f'{self.ShiftName} ({self.ShiftCode})'

class EmployeeRoster(TimeStampedModel):
    RosterKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    DutyDate = models.DateField(db_index=True)
    Shift = models.ForeignKey(ShiftMaster, on_delete=models.PROTECT, db_column='ShiftKey')
    IsOffDay = models.BooleanField(default=False)
    IsHoliday = models.BooleanField(default=False)

    class Meta:
        db_table = 'EmployeeRoster'
        unique_together = (('EmpKey', 'DutyDate'),)
