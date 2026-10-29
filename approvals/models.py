from django.db import models
from core.models import TimeStampedModel
from organization.models import Company

class ApprovalTier(TimeStampedModel):
    TierKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.CASCADE, db_column='CompanyKey')
    DocumentType = models.CharField(max_length=50, db_index=True)
    TierLevel = models.IntegerField(default=1)
    RoleCode = models.CharField(max_length=50)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'ApprovalTier'
        unique_together = (('Company', 'DocumentType', 'TierLevel'),)

class ApprovalRequest(TimeStampedModel):
    RequestKey = models.BigAutoField(primary_key=True)
    DocumentType = models.CharField(max_length=50, db_index=True)
    RecordPK = models.CharField(max_length=100, db_index=True)
    CurrentTierLevel = models.IntegerField(default=1)
    Status = models.CharField(max_length=30, default='PENDING')
    InitiatedByEmpKey = models.BigIntegerField(db_index=True)
    CurrentApproverEmpKey = models.BigIntegerField(null=True, blank=True, db_index=True)
    Remarks = models.TextField(null=True, blank=True)
    class Meta:
        db_table = 'ApprovalRequest'
