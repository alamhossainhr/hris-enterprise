from django.db import models
from core.models import TimeStampedModel

class EmployeeInfoDetails(models.Model):
    EmpKey = models.BigAutoField(primary_key=True, db_column='EmpKey')
    EmpCode = models.CharField(max_length=50, unique=True, db_column='EmpCode')
    CardNo = models.CharField(max_length=50, null=True, blank=True, db_column='CardNo')
    EmpName = models.CharField(max_length=150, db_column='EmpName')
    Gender = models.CharField(max_length=20, null=True, blank=True, db_column='Gender')
    DOB = models.DateField(null=True, blank=True, db_column='DOB')
    DOJ = models.DateField(null=True, blank=True, db_column='DOJ')
    DOC = models.DateField(null=True, blank=True, db_column='DOC')
    CompanyID = models.BigIntegerField(null=True, blank=True, db_column='CompanyID')
    DepartmentID = models.BigIntegerField(null=True, blank=True, db_column='DepartmentID')
    SectionID = models.BigIntegerField(null=True, blank=True, db_column='SectionID')
    LineID = models.BigIntegerField(null=True, blank=True, db_column='LineID')
    DesignationID = models.BigIntegerField(null=True, blank=True, db_column='DesignationID')
    GradeID = models.BigIntegerField(null=True, blank=True, db_column='GradeID')
    GrossSalary = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='GrossSalary')
    BasicSalary = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='BasicSalary')
    HouseRent = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='HouseRent')
    Medical = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='Medical')
    Food = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='Food')
    Conveyance = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, db_column='Conveyance')
    OTAllowed = models.BooleanField(default=True, db_column='OTAllowed')
    IsActive = models.BooleanField(default=True, db_column='IsActive')
    EmployeeStatus = models.CharField(max_length=30, default='Active', db_column='EmployeeStatus')
    SeparationDate = models.DateField(null=True, blank=True, db_column='SeparationDate')
    BloodGroup = models.CharField(max_length=10, null=True, blank=True, db_column='BloodGroup')
    NID = models.CharField(max_length=50, null=True, blank=True, db_column='NID')
    Mobile = models.CharField(max_length=30, null=True, blank=True, db_column='Mobile')
    class Meta:
        db_table = 'EmployeeInfoDetails'
        managed = False
    def __str__(self):
        return f'{self.EmpCode} - {self.EmpName}'

class EmployeeExtendedProfile(TimeStampedModel):
    EmpKey = models.BigIntegerField(primary_key=True, db_column='EmpKey')
    EmpNameBangla = models.CharField(max_length=200, null=True, blank=True)
    FatherName = models.CharField(max_length=150, null=True, blank=True)
    MotherName = models.CharField(max_length=150, null=True, blank=True)
    SpouseName = models.CharField(max_length=150, null=True, blank=True)
    PresentAddress = models.TextField(null=True, blank=True)
    PermanentAddress = models.TextField(null=True, blank=True)
    EmergencyContactName = models.CharField(max_length=150, null=True, blank=True)
    EmergencyContactPhone = models.CharField(max_length=50, null=True, blank=True)
    EmergencyContactRelation = models.CharField(max_length=50, null=True, blank=True)
    BankName = models.CharField(max_length=100, null=True, blank=True)
    BranchName = models.CharField(max_length=100, null=True, blank=True)
    BankAccountNo = models.CharField(max_length=50, null=True, blank=True)
    RoutingNumber = models.CharField(max_length=50, null=True, blank=True)
    MobileBankingProvider = models.CharField(max_length=50, null=True, blank=True)
    MobileBankingNumber = models.CharField(max_length=50, null=True, blank=True)
    PaymentMode = models.CharField(max_length=30, default='Bank')
    Photo = models.ImageField(upload_to='employees/photos/', null=True, blank=True)
    Signature = models.ImageField(upload_to='employees/signatures/', null=True, blank=True)
    class Meta:
        db_table = 'EmployeeExtendedProfile'

class DigitalServiceBook(TimeStampedModel):
    EventKey = models.BigAutoField(primary_key=True)
    EmpKey = models.BigIntegerField(db_index=True)
    EventType = models.CharField(max_length=50, db_index=True)
    EffectiveDate = models.DateField()
    PreviousCompanyID = models.BigIntegerField(null=True, blank=True)
    NewCompanyID = models.BigIntegerField(null=True, blank=True)
    PreviousDepartmentID = models.BigIntegerField(null=True, blank=True)
    NewDepartmentID = models.BigIntegerField(null=True, blank=True)
    PreviousDesignationID = models.BigIntegerField(null=True, blank=True)
    NewDesignationID = models.BigIntegerField(null=True, blank=True)
    PreviousSalary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    NewSalary = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    Remarks = models.TextField(null=True, blank=True)
    ApprovedBy = models.CharField(max_length=100, null=True, blank=True)
    class Meta:
        db_table = 'DigitalServiceBook'
        ordering = ['-EffectiveDate', '-EventKey']
