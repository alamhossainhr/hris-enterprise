from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from organization.models import Enterprise, Company, FactoryUnit, Department, Section, Line, Designation
from organization.forms import EnterpriseForm, CompanyForm, DepartmentForm, DesignationForm

def org_tree(request):
    enterprises = Enterprise.objects.prefetch_related('companies__departments__sections__lines').all()
    companies = Company.objects.all()
    departments = Department.objects.select_related('Company').all()
    designations = Designation.objects.select_related('Grade').all()
    return render(request, 'organization/tree.html', {
        'enterprises': enterprises,
        'companies': companies,
        'departments': departments,
        'designations': designations,
    })

def company_create(request):
    if request.method == 'POST':
        form = CompanyForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Company created successfully.')
            return redirect('org_tree')
    else:
        form = CompanyForm()
    return render(request, 'organization/form.html', {'form': form, 'title': 'Create Company'})

def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully.')
            return redirect('org_tree')
    else:
        form = DepartmentForm()
    return render(request, 'organization/form.html', {'form': form, 'title': 'Create Department'})

def designation_create(request):
    if request.method == 'POST':
        form = DesignationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Designation created successfully.')
            return redirect('org_tree')
    else:
        form = DesignationForm()
    return render(request, 'organization/form.html', {'form': form, 'title': 'Create Designation'})
