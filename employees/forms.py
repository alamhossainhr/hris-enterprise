from django import forms
from employees.models import EmployeeExtendedProfile, DigitalServiceBook
from documents.models import EmployeeDocument

class EmployeeExtendedProfileForm(forms.ModelForm):
    class Meta:
        model = EmployeeExtendedProfile
        fields = [
            'EmpNameBangla', 'FatherName', 'MotherName', 'SpouseName',
            'PresentAddress', 'PermanentAddress', 'EmergencyContactName',
            'EmergencyContactPhone', 'EmergencyContactRelation', 'BankName',
            'BranchName', 'BankAccountNo', 'RoutingNumber', 'MobileBankingProvider',
            'MobileBankingNumber', 'PaymentMode', 'Photo', 'Signature'
        ]
        widgets = {
            'EmpNameBangla': forms.TextInput(attrs={'class': 'form-control'}),
            'FatherName': forms.TextInput(attrs={'class': 'form-control'}),
            'MotherName': forms.TextInput(attrs={'class': 'form-control'}),
            'SpouseName': forms.TextInput(attrs={'class': 'form-control'}),
            'PresentAddress': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'PermanentAddress': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'EmergencyContactName': forms.TextInput(attrs={'class': 'form-control'}),
            'EmergencyContactPhone': forms.TextInput(attrs={'class': 'form-control'}),
            'EmergencyContactRelation': forms.TextInput(attrs={'class': 'form-control'}),
            'BankName': forms.TextInput(attrs={'class': 'form-control'}),
            'BranchName': forms.TextInput(attrs={'class': 'form-control'}),
            'BankAccountNo': forms.TextInput(attrs={'class': 'form-control'}),
            'RoutingNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'MobileBankingProvider': forms.TextInput(attrs={'class': 'form-control'}),
            'MobileBankingNumber': forms.TextInput(attrs={'class': 'form-control'}),
            'PaymentMode': forms.Select(choices=[('Bank', 'Bank'), ('Cash', 'Cash'), ('bKash', 'bKash'), ('Nagad', 'Nagad'), ('Rocket', 'Rocket')], attrs={'class': 'form-select'}),
            'Photo': forms.FileInput(attrs={'class': 'form-control'}),
            'Signature': forms.FileInput(attrs={'class': 'form-control'}),
        }

class ServiceBookEventForm(forms.ModelForm):
    class Meta:
        model = DigitalServiceBook
        fields = ['EventType', 'EffectiveDate', 'PreviousSalary', 'NewSalary', 'Remarks', 'ApprovedBy']
        widgets = {
            'EventType': forms.Select(choices=[('JOIN', 'Joining'), ('CONFIRMATION', 'Confirmation'), ('PROMOTION', 'Promotion'), ('INCREMENT', 'Increment'), ('TRANSFER', 'Transfer'), ('SEPARATION', 'Separation')], attrs={'class': 'form-select'}),
            'EffectiveDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'PreviousSalary': forms.NumberInput(attrs={'class': 'form-control'}),
            'NewSalary': forms.NumberInput(attrs={'class': 'form-control'}),
            'Remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ApprovedBy': forms.TextInput(attrs={'class': 'form-control'}),
        }

class EmployeeDocumentForm(forms.ModelForm):
    class Meta:
        model = EmployeeDocument
        fields = ['DocType', 'DocumentTitle', 'Attachment', 'IssueDate', 'ExpiryDate', 'Remarks']
        widgets = {
            'DocType': forms.Select(attrs={'class': 'form-select'}),
            'DocumentTitle': forms.TextInput(attrs={'class': 'form-control'}),
            'Attachment': forms.FileInput(attrs={'class': 'form-control'}),
            'IssueDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'ExpiryDate': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'Remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }
