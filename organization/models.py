from django.db import models
from core.models import TimeStampedModel

class Enterprise(TimeStampedModel):
    EnterpriseKey = models.BigAutoField(primary_key=True)
    EnterpriseCode = models.CharField(max_length=50, unique=True)
    EnterpriseName = models.CharField(max_length=200)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'EnterpriseInfo'
    def __str__(self):
        return self.EnterpriseName

class Company(TimeStampedModel):
    CompanyKey = models.BigAutoField(primary_key=True)
    Enterprise = models.ForeignKey(Enterprise, on_delete=models.PROTECT, related_name='companies', db_column='EnterpriseKey')
    CompanyCode = models.CharField(max_length=50, unique=True)
    CompanyName = models.CharField(max_length=250)
    ShortName = models.CharField(max_length=50)
    BIN = models.CharField(max_length=50, null=True, blank=True)
    TIN = models.CharField(max_length=50, null=True, blank=True)
    CorporateAddress = models.TextField(null=True, blank=True)
    FactoryAddress = models.TextField(null=True, blank=True)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'CompanyInfo'
    def __str__(self):
        return self.CompanyName

class FactoryUnit(TimeStampedModel):
    UnitKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='factory_units', db_column='CompanyKey')
    UnitCode = models.CharField(max_length=50)
    UnitName = models.CharField(max_length=200)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'FactoryUnitInfo'
        unique_together = (('Company', 'UnitCode'),)
    def __str__(self):
        return f'{self.Company.ShortName} - {self.UnitName}'

class Department(TimeStampedModel):
    DepartmentKey = models.BigAutoField(primary_key=True)
    Company = models.ForeignKey(Company, on_delete=models.PROTECT, related_name='departments', db_column='CompanyKey')
    DepartmentCode = models.CharField(max_length=50)
    DepartmentName = models.CharField(max_length=200)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'DepartmentInfo'
        unique_together = (('Company', 'DepartmentCode'),)
    def __str__(self):
        return self.DepartmentName

class Section(TimeStampedModel):
    SectionKey = models.BigAutoField(primary_key=True)
    Department = models.ForeignKey(Department, on_delete=models.PROTECT, related_name='sections', db_column='DepartmentKey')
    SectionCode = models.CharField(max_length=50)
    SectionName = models.CharField(max_length=200)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'SectionInfo'
        unique_together = (('Department', 'SectionCode'),)
    def __str__(self):
        return f'{self.Department.DepartmentName} -> {self.SectionName}'

class Line(TimeStampedModel):
    LineKey = models.BigAutoField(primary_key=True)
    Section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name='lines', db_column='SectionKey')
    LineCode = models.CharField(max_length=50)
    LineName = models.CharField(max_length=150)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'LineInfo'
        unique_together = (('Section', 'LineCode'),)
    def __str__(self):
        return f'{self.Section.SectionName} -> {self.LineName}'

class DesignationGrade(TimeStampedModel):
    GradeKey = models.BigAutoField(primary_key=True)
    GradeCode = models.CharField(max_length=30, unique=True)
    GradeName = models.CharField(max_length=100)
    MinimumSalary = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    MaximumSalary = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'DesignationGradeInfo'
    def __str__(self):
        return self.GradeName

class Designation(TimeStampedModel):
    DesignationKey = models.BigAutoField(primary_key=True)
    Grade = models.ForeignKey(DesignationGrade, on_delete=models.PROTECT, null=True, blank=True, db_column='GradeKey')
    DesignationCode = models.CharField(max_length=50, unique=True)
    DesignationName = models.CharField(max_length=150)
    IsActive = models.BooleanField(default=True)
    class Meta:
        db_table = 'DesignationInfo'
    def __str__(self):
        return self.DesignationName
