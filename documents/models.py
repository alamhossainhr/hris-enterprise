from django.db import models
from core.models import TimeStampedModel

class DocumentTypeMaster(TimeStampedModel):
    TypeKey = models.BigAutoField(primary_key=True)
    TypeCode = models.CharField(max_length=50, unique=True)
    TypeName = models.CharField(max_length=100)
    IsMandatory = models.BooleanField(default=False)
    class Meta:
        db_table = 'DocumentTypeMaster'
    def __str__(self):
        return self.TypeName

class EmployeeDocument(TimeStampedModel):
    DocKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    DocType = models.ForeignKey(DocumentTypeMaster, on_delete=models.PROTECT, db_column='TypeKey')
    DocumentTitle = models.CharField(max_length=200)
    Attachment = models.FileField(upload_to='employees/documents/%Y/%m/')
    IssueDate = models.DateField(null=True, blank=True)
    ExpiryDate = models.DateField(null=True, blank=True)
    Remarks = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'EmployeeDocuments'
