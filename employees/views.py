from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from employees.models import EmployeeInfoDetails, EmployeeExtendedProfile, DigitalServiceBook
from employees.forms import EmployeeExtendedProfileForm, ServiceBookEventForm, EmployeeDocumentForm
from employees.services.service_book_service import ServiceBookService
from documents.models import EmployeeDocument, DocumentTypeMaster

def employee_list(request):
    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'Active')
    employees = EmployeeInfoDetails.objects.all()
    if status_filter:
        employees = employees.filter(EmployeeStatus=status_filter)
    if search_query:
        employees = employees.filter(
            Q(EmpCode__icontains=search_query) |
            Q(EmpName__icontains=search_query) |
            Q(NID__icontains=search_query) |
            Q(Mobile__icontains=search_query)
        )
    paginator = Paginator(employees.order_by('EmpCode'), 25)
    page_obj = paginator.get_page(request.GET.get('page', 1))
    return render(request, 'employees/employee_list.html', {
        'page_obj': page_obj,
        'search_query': search_query,
        'status_filter': status_filter
    })

def employee_profile(request, emp_key):
    employee = get_object_or_404(EmployeeInfoDetails, EmpKey=emp_key)
    profile, _ = EmployeeExtendedProfile.objects.get_or_create(EmpKey=emp_key)
    service_records = DigitalServiceBook.objects.filter(EmpKey=emp_key).order_by('-EffectiveDate')
    documents = EmployeeDocument.objects.filter(EmpKey=emp_key).select_related('DocType')
    doc_types = DocumentTypeMaster.objects.all()
    return render(request, 'employees/employee_profile.html', {
        'emp': employee,
        'profile': profile,
        'service_records': service_records,
        'documents': documents,
        'doc_types': doc_types,
    })

def employee_profile_edit(request, emp_key):
    employee = get_object_or_404(EmployeeInfoDetails, EmpKey=emp_key)
    profile, _ = EmployeeExtendedProfile.objects.get_or_create(EmpKey=emp_key)
    if request.method == 'POST':
        form = EmployeeExtendedProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile details updated successfully.')
            return redirect('employee_profile', emp_key=emp_key)
    else:
        form = EmployeeExtendedProfileForm(instance=profile)
    return render(request, 'employees/profile_edit.html', {'form': form, 'emp': employee})

def add_service_event(request, emp_key):
    employee = get_object_or_404(EmployeeInfoDetails, EmpKey=emp_key)
    if request.method == 'POST':
        form = ServiceBookEventForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            ServiceBookService.record_event(
                emp_key=emp_key,
                event_type=data['EventType'],
                effective_date=data['EffectiveDate'],
                prev_salary=data['PreviousSalary'],
                new_salary=data['NewSalary'],
                remarks=data['Remarks'],
                approved_by=data['ApprovedBy'],
                user=request.user.username if request.user.is_authenticated else 'SYSTEM'
            )
            messages.success(request, 'Digital service event registered successfully.')
            return redirect('employee_profile', emp_key=emp_key)
    else:
        form = ServiceBookEventForm(initial={'PreviousSalary': employee.GrossSalary})
    return render(request, 'employees/event_form.html', {'form': form, 'emp': employee})

def upload_document(request, emp_key):
    employee = get_object_or_404(EmployeeInfoDetails, EmpKey=emp_key)
    if request.method == 'POST':
        form = EmployeeDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.EmpKey = emp_key
            doc.save()
            messages.success(request, 'Document uploaded successfully.')
            return redirect('employee_profile', emp_key=emp_key)
    else:
        form = EmployeeDocumentForm()
    return render(request, 'employees/document_upload.html', {'form': form, 'emp': employee})
