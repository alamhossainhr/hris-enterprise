from django.db import models
from core.models import TimeStampedModel

class AttendanceStatusMaster(TimeStampedModel):
    StatusKey = models.BigAutoField(primary_key=True)
    StatusCode = models.CharField(max_length=10, unique=True) # P, A, L, LV, W, H, PW, PH
    StatusName = models.CharField(max_length=50)
    IsPayable = models.BooleanField(default=True)
    IsPresentEquivalent = models.BooleanField(default=False)
    ColorCode = models.CharField(max_length=20, default='#198754')

    class Meta:
        db_table = 'AttendanceStatusMaster'

    def __str__(self):
        return f'{self.StatusCode} - {self.StatusName}'

class AttendanceRawPunch(models.Model):
    PunchKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    MachineEmployeeID = models.CharField(max_length=50, null=True, blank=True, db_index=True)
    PunchDateTime = models.DateTimeField(db_index=True)
    DeviceID = models.CharField(max_length=50, default='MANUAL')
    DeviceIP = models.GenericIPAddressField(null=True, blank=True)
    Source = models.CharField(max_length=30, default='DEVICE') # DEVICE, EXCEL, MANUAL
    ImportBatchID = models.CharField(max_length=50, null=True, blank=True)
    ImportedAt = models.DateTimeField(auto_now_add=True)
    Processed = models.BooleanField(default=False, db_index=True)

    class Meta:
        db_table = 'AttendanceRawPunch'
        ordering = ['PunchDateTime']

class AttendanceAdjustmentLog(TimeStampedModel):
    AdjustmentKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    WorkDate = models.DateField(db_index=True)
    TargetTable = models.CharField(max_length=20)
    OldInTime = models.TimeField(null=True, blank=True)
    NewInTime = models.TimeField(null=True, blank=True)
    OldOutTime = models.TimeField(null=True, blank=True)
    NewOutTime = models.TimeField(null=True, blank=True)
    OldDayStatus = models.CharField(max_length=10, null=True, blank=True)
    NewDayStatus = models.CharField(max_length=10)
    OldOTHour = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    NewOTHour = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    Reason = models.TextField()
    ApprovedBy = models.CharField(max_length=100)

    class Meta:
        db_table = 'AttendanceAdjustmentLog'
