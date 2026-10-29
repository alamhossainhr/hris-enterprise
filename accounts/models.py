from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from core.models import TimeStampedModel
from organization.models import Company, Department

class UserAccountManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username field is mandatory.')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(username, email, password, **extra_fields)

class RoleMaster(TimeStampedModel):
    RoleKey = models.BigAutoField(primary_key=True)
    RoleCode = models.CharField(max_length=50, unique=True)
    RoleName = models.CharField(max_length=100)
    Description = models.TextField(blank=True, null=True)
    IsSystemRole = models.BooleanField(default=False)
    class Meta:
        db_table = 'RoleMaster'
    def __str__(self):
        return self.RoleName

class ModuleManager(TimeStampedModel):
    ModuleKey = models.BigAutoField(primary_key=True)
    ModuleCode = models.CharField(max_length=50, unique=True)
    ModuleName = models.CharField(max_length=100)
    IconClass = models.CharField(max_length=100, default='bi-box')
    SortOrder = models.IntegerField(default=0)
    IsEnabled = models.BooleanField(default=True)
    class Meta:
        db_table = 'ModuleManager'
        ordering = ['SortOrder']
    def __str__(self):
        return self.ModuleName

class PermissionMatrix(TimeStampedModel):
    PermissionKey = models.BigAutoField(primary_key=True)
    Role = models.ForeignKey(RoleMaster, on_delete=models.CASCADE, related_name='permissions', db_column='RoleKey')
    Module = models.ForeignKey(ModuleManager, on_delete=models.CASCADE, related_name='module_permissions', db_column='ModuleKey')
    CanView = models.BooleanField(default=False)
    CanAdd = models.BooleanField(default=False)
    CanEdit = models.BooleanField(default=False)
    CanDelete = models.BooleanField(default=False)
    CanApprove = models.BooleanField(default=False)
    CanReject = models.BooleanField(default=False)
    CanExport = models.BooleanField(default=False)
    CanPrint = models.BooleanField(default=False)
    class Meta:
        db_table = 'PermissionMatrix'
        unique_together = (('Role', 'Module'),)

class UserAccount(AbstractBaseUser, PermissionsMixin):
    UserKey = models.BigAutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(max_length=255, unique=True)
    EmpKey = models.BigIntegerField(null=True, blank=True, db_index=True)
    Company = models.ForeignKey(Company, null=True, blank=True, on_delete=models.SET_NULL, db_column='CompanyKey')
    Department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, db_column='DepartmentKey')
    Roles = models.ManyToManyField(RoleMaster, related_name='users', blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    failed_login_count = models.IntegerField(default=0)
    is_locked = models.BooleanField(default=False)
    objects = UserAccountManager()
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    class Meta:
        db_table = 'UserAccounts'
    def __str__(self):
        return f'{self.username} ({self.email})'
