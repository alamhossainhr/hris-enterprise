from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from shifts.models import ShiftMaster
from shifts.forms import ShiftMasterForm

def shift_list(request):
    shifts = ShiftMaster.objects.select_related('Company').all()
    return render(request, 'shifts/shift_list.html', {'shifts': shifts})

def shift_create(request):
    if request.method == 'POST':
        form = ShiftMasterForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Shift configuration saved successfully.')
            return redirect('shift_list')
    else:
        form = ShiftMasterForm()
    return render(request, 'shifts/shift_form.html', {'form': form, 'title': 'Define Enterprise Shift'})
