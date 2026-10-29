from django import forms
from organization.models import Enterprise, Company, FactoryUnit, Department, Section, Line, DesignationGrade, Designation

class EnterpriseForm(forms.ModelForm):
    class Meta:
        model = Enterprise
        fields = ['EnterpriseCode', 'EnterpriseName', 'IsActive']
        widgets = {
            'EnterpriseCode': forms.TextInput(attrs={'class': 'form-control'}),
            'EnterpriseName': forms.TextInput(attrs={'class': 'form-control'}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['Enterprise', 'CompanyCode', 'CompanyName', 'ShortName', 'BIN', 'TIN', 'CorporateAddress', 'FactoryAddress', 'IsActive']
        widgets = {
            'Enterprise': forms.Select(attrs={'class': 'form-select'}),
            'CompanyCode': forms.TextInput(attrs={'class': 'form-control'}),
            'CompanyName': forms.TextInput(attrs={'class': 'form-control'}),
            'ShortName': forms.TextInput(attrs={'class': 'form-control'}),
            'BIN': forms.TextInput(attrs={'class': 'form-control'}),
            'TIN': forms.TextInput(attrs={'class': 'form-control'}),
            'CorporateAddress': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'FactoryAddress': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ['Company', 'DepartmentCode', 'DepartmentName', 'IsActive']
        widgets = {
            'Company': forms.Select(attrs={'class': 'form-select'}),
            'DepartmentCode': forms.TextInput(attrs={'class': 'form-control'}),
            'DepartmentName': forms.TextInput(attrs={'class': 'form-control'}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class DesignationForm(forms.ModelForm):
    class Meta:
        model = Designation
        fields = ['Grade', 'DesignationCode', 'DesignationName', 'IsActive']
        widgets = {
            'Grade': forms.Select(attrs={'class': 'form-select'}),
            'DesignationCode': forms.TextInput(attrs={'class': 'form-control'}),
            'DesignationName': forms.TextInput(attrs={'class': 'form-control'}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
