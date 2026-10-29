import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from attendance.models import AttendanceRawPunch, AttendanceAdjustmentLog, AttendanceStatusMaster
from attendance.services.table_service import AttendanceTableService
from attendance.repositories.monthly_attendance_repository import MonthlyAttendanceRepository
from attendance.services.attendance_processor import AttendanceProcessingEngine
from employees.models import EmployeeInfoDetails
from audit.models import SystemAuditTrail
from django.db import connection

def attendance_query_console(request):
    from_date_str = request.GET.get('from_date')
    to_date_str = request.GET.get('to_date')
    emp_keys_str = request.GET.get('emp_keys', '').strip()
    today = datetime.date.today()
    from_date = datetime.datetime.strptime(from_date_str, '%Y-%m-%d').date() if from_date_str else today.replace(day=1)
    to_date = datetime.datetime.strptime(to_date_str, '%Y-%m-%d').date() if to_date_str else today

    emp_keys = [int(k.strip()) for k in emp_keys_str.split(',') if k.strip().isdigit()] if emp_keys_str else None
    intervals = AttendanceTableService.get_tables_between_dates(from_date, to_date)
    records = MonthlyAttendanceRepository.fetch_attendance_range(from_date, to_date, emp_keys)

    return render(request, 'attendance/query_console.html', {
        'from_date': from_date.strftime('%Y-%m-%d'),
        'to_date': to_date.strftime('%Y-%m-%d'),
        'emp_keys_str': emp_keys_str,
        'intervals': intervals,
        'attendance_records': records,
    })

def attendance_process_view(request):
    if request.method == 'POST':
        from_date = datetime.datetime.strptime(request.POST['from_date'], '%Y-%m-%d').date()
        to_date = datetime.datetime.strptime(request.POST['to_date'], '%Y-%m-%d').date()
        res = AttendanceProcessingEngine.process_date_range(from_date, to_date)
        messages.success(request, f"Processed {res['days_processed']} day(s). Updated {res['records_computed']} employee records.")
        return redirect('attendance_query_console')
    return render(request, 'attendance/process_form.html')

def raw_punch_manual(request):
    if request.method == 'POST':
        emp_code = request.POST['emp_code'].strip()
        punch_dt = request.POST['punch_datetime']
        emp = EmployeeInfoDetails.objects.filter(EmpCode=emp_code).first()
        if not emp:
            messages.error(request, f'Employee code {emp_code} not found.')
        else:
            AttendanceRawPunch.objects.create(
                EmpKey=emp.EmpKey,
                MachineEmployeeID=emp_code,
                PunchDateTime=punch_dt,
                Source='MANUAL'
            )
            messages.success(request, f'Punch ingested for {emp.EmpName} ({emp_code})')
            return redirect('attendance_query_console')
    return render(request, 'attendance/punch_form.html')
