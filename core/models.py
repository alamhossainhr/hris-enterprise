from django.db import models

class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, db_column='DateAdded')
    updated_at = models.DateTimeField(auto_now=True, db_column='DateUpdated')
    created_by = models.CharField(max_length=100, null=True, blank=True, db_column='AddedBy')
    updated_by = models.CharField(max_length=100, null=True, blank=True, db_column='UpdatedBy')

    class Meta:
        abstract = True
