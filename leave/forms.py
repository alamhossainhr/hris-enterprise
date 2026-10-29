from django import forms
from leave.models import LeaveTypeMaster, LeaveApplication, MaternityBenefitRecord

class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ["LeaveType", "FromDate", "ToDate", "Reason"]
        widgets = {
            "LeaveType": forms.Select(attrs={"class": "form-select"}),
            "FromDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "ToDate": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "Reason": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
        }

class MaternityApplicationForm(forms.Form):
    EmpKey = forms.IntegerField(widget=forms.HiddenInput())
    EDD = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
    LeaveStartDate = forms.DateField(widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}))
