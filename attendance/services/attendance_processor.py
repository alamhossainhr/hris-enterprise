import datetime
from django.db import connection, transaction
from attendance.models import AttendanceRawPunch, AttendanceStatusMaster
from attendance.services.table_service import AttendanceTableService
from shifts.models import ShiftMaster, EmployeeRoster
from employees.models import EmployeeInfoDetails

class AttendanceProcessingEngine:
    @classmethod
    def process_date_range(cls, from_date: datetime.date, to_date: datetime.date, emp_keys: list[int] = None) -> dict:
        intervals = AttendanceTableService.get_tables_between_dates(from_date, to_date)
        for item in intervals:
            year = int(item['table'][:4])
            month = int(item['table'][4:])
            AttendanceTableService.create_monthly_attendance_table(year, month)

        total_processed = 0
        curr = from_date
        while curr <= to_date:
            total_processed += cls._process_single_day(curr, emp_keys)
            curr += datetime.timedelta(days=1)
        return {'status': 'SUCCESS', 'days_processed': (to_date - from_date).days + 1, 'records_computed': total_processed}

    @classmethod
    def _process_single_day(cls, work_date: datetime.date, emp_keys: list[int] = None) -> int:
        table_name = AttendanceTableService.get_table_name(work_date)
        AttendanceTableService.validate_table_name(table_name)

        emp_qs = EmployeeInfoDetails.objects.filter(IsActive=True, DOJ__lte=work_date)
        if emp_keys:
            emp_qs = emp_qs.filter(EmpKey__in=emp_keys)

        processed_count = 0
        default_shift = ShiftMaster.objects.filter(IsActive=True).first()

        for emp in emp_qs:
            roster = EmployeeRoster.objects.filter(EmpKey=emp.EmpKey, DutyDate=work_date).select_related('Shift').first()
            shift = roster.Shift if roster else default_shift
            if not shift:
                continue

            # Compute Shift Window including cross-midnight
            shift_start_dt = datetime.datetime.combine(work_date, shift.StartTime)
            if shift.IsCrossMidnight or shift.EndTime < shift.StartTime:
                shift_end_dt = datetime.datetime.combine(work_date + datetime.timedelta(days=1), shift.EndTime)
            else:
                shift_end_dt = datetime.datetime.combine(work_date, shift.EndTime)

            window_start = shift_start_dt - datetime.timedelta(hours=3)
            window_end = shift_end_dt + datetime.timedelta(hours=6)

            # Ingest Raw Punches in Window
            punches = list(AttendanceRawPunch.objects.filter(
                EmpKey=emp.EmpKey,
                PunchDateTime__range=(window_start, window_end)
            ).order_by('PunchDateTime').values_list('PunchDateTime', flat=True))

            in_time = punches[0] if punches else None
            out_time = punches[-1] if (punches and len(punches) > 1) else None

            # Determine Status, Late, Early Exit, OT
            late_minutes = 0
            early_exit_minutes = 0
            ot_hours = 0.0
            day_status = 'A'

            if roster and roster.IsOffDay:
                day_status = 'PW' if in_time else 'W'
            elif roster and roster.IsHoliday:
                day_status = 'PH' if in_time else 'H'
            elif in_time:
                day_status = 'P'
                if in_time > (shift_start_dt + datetime.timedelta(minutes=shift.GraceInMinutes)):
                    late_minutes = int((in_time - shift_start_dt).total_seconds() // 60)
                    if late_minutes > shift.LateThresholdMinutes:
                        day_status = 'L'

                if out_time and emp.OTAllowed:
                    ot_threshold = shift_end_dt + datetime.timedelta(minutes=shift.OTStartMinutesAfterShift)
                    if out_time > ot_threshold:
                        ot_seconds = (out_time - shift_end_dt).total_seconds()
                        ot_hours = round(ot_seconds / 3600.0, 2)

            # Upsert into Dynamic Table [YYYYM]
            cls._upsert_attendance_record(
                table_name=table_name,
                emp_key=emp.EmpKey,
                work_date=work_date,
                shift_id=shift.ShiftKey,
                in_time=in_time.strftime('%H:%M:%S') if in_time else None,
                out_time=out_time.strftime('%H:%M:%S') if out_time else None,
                day_status=day_status,
                late_minute=late_minutes,
                early_exit_minute=early_exit_minutes,
                ot_hour=ot_hours
            )
            processed_count += 1
        return processed_count

    @classmethod
    def _upsert_attendance_record(cls, table_name: str, emp_key: int, work_date: datetime.date, shift_id: int, in_time, out_time, day_status, late_minute, early_exit_minute, ot_hour):
        with connection.cursor() as cursor:
            # Check existing
            cursor.execute(f'SELECT AttKey FROM [{table_name}] WHERE EmpKey = %s AND WorkDate = %s', [emp_key, work_date])
            row = cursor.fetchone()
            if row:
                cursor.execute(f'''
                    UPDATE [{table_name}]
                    SET ShiftID = %s, InTime = %s, OutTime = %s, DayStatus = %s,
                        LateMinute = %s, EarlyExitMinute = %s, OTHour = %s, DateUpdated = GETDATE()
                    WHERE AttKey = %s
                ''', [shift_id, in_time, out_time, day_status, late_minute, early_exit_minute, ot_hour, row[0]])
            else:
                # Generate simple pseudo-key for legacy table without auto-increment PK
                att_key = int(f"{emp_key}{work_date.strftime('%y%m%d')}")
                cursor.execute(f'''
                    INSERT INTO [{table_name}] (
                        AttKey, EmpKey, WorkDate, ShiftID, InTime, OutTime, DayStatus,
                        LateMinute, EarlyExitMinute, PayHour, OTHour, EOT, NightDays, DateAdded
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 8.0, %s, 0.0, 0, GETDATE())
                ''', [att_key, emp_key, work_date, shift_id, in_time, out_time, day_status, late_minute, early_exit_minute, ot_hour])
