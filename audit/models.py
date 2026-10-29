from django.db import models

class SystemAuditTrail(models.Model):
    AuditKey = models.BigAutoField(primary_key=True)
    UserKey = models.BigIntegerField(null=True, blank=True, db_index=True)
    Username = models.CharField(max_length=150, db_index=True)
    EmpKey = models.BigIntegerField(null=True, blank=True, db_index=True)
    ModuleName = models.CharField(max_length=100, db_index=True)
    Action = models.CharField(max_length=50)
    TableName = models.CharField(max_length=100, db_index=True)
    RecordKey = models.CharField(max_length=100)
    FieldName = models.CharField(max_length=100, null=True, blank=True)
    OldValue = models.TextField(null=True, blank=True)
    NewValue = models.TextField(null=True, blank=True)
    Reason = models.TextField(null=True, blank=True)
    IPAddress = models.GenericIPAddressField(null=True, blank=True)
    UserAgent = models.TextField(null=True, blank=True)
    Timestamp = models.DateTimeField(auto_now_add=True, db_index=True)
    class Meta:
        db_table = 'SystemAuditTrail'
        ordering = ['-Timestamp']
