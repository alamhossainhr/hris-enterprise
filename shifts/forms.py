from django import forms
from shifts.models import ShiftMaster, EmployeeRoster

class ShiftMasterForm(forms.ModelForm):
    class Meta:
        model = ShiftMaster
        fields = ['Company', 'ShiftCode', 'ShiftName', 'StartTime', 'EndTime', 'GraceInMinutes', 'LateThresholdMinutes', 'EarlyExitThresholdMinutes', 'BreakMinutes', 'OTStartMinutesAfterShift', 'IsCrossMidnight', 'IsActive']
        widgets = {
            'Company': forms.Select(attrs={'class': 'form-select'}),
            'ShiftCode': forms.TextInput(attrs={'class': 'form-control'}),
            'ShiftName': forms.TextInput(attrs={'class': 'form-control'}),
            'StartTime': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'EndTime': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'GraceInMinutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'LateThresholdMinutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'EarlyExitThresholdMinutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'BreakMinutes': forms.NumberInput(attrs={'class': 'form-control'}),
            'OTStartMinutesAfterShift': forms.NumberInput(attrs={'class': 'form-control'}),
            'IsCrossMidnight': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'IsActive': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
