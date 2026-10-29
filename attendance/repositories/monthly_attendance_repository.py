from django.db import connection
from attendance.services.table_service import AttendanceTableService

class MonthlyAttendanceRepository:
    @classmethod
    def fetch_attendance_range(cls, from_date, to_date, emp_keys: list[int] = None) -> list[dict]:
        intervals = AttendanceTableService.get_tables_between_dates(from_date, to_date)
        if not intervals:
            return []
        union_queries = []
        params = []
        for item in intervals:
            table = item["table"]
            if not AttendanceTableService.table_exists(table):
                continue
            emp_clause = ""
            if emp_keys:
                placeholders = ",".join(["%s"] * len(emp_keys))
                emp_clause = f"AND Att.EmpKey IN ({placeholders})"
            sub_query = f"""
                SELECT 
                    Att.AttKey, Att.EmpKey, E.EmpCode, E.EmpName, Att.WorkDate,
                    Att.ShiftID, Att.InTime, Att.OutTime, Att.DayStatus,
                    Att.LateMinute, Att.EarlyExitMinute, Att.PayHour,
                    Att.OTHour, Att.EOT, Att.NightDays, Att.Remarks
                FROM [{table}] Att WITH (NOLOCK)
                INNER JOIN EmployeeInfoDetails E WITH (NOLOCK) ON Att.EmpKey = E.EmpKey
                WHERE Att.WorkDate BETWEEN %s AND %s {emp_clause}
            """
            union_queries.append(sub_query)
            params.extend([item["start"], item["end"]])
            if emp_keys:
                params.extend(emp_keys)
        if not union_queries:
            return []
        final_sql = " UNION ALL ".join(union_queries) + " ORDER BY WorkDate ASC, EmpKey ASC"
        with connection.cursor() as cursor:
            cursor.execute(final_sql, params)
            columns = [col[0] for col in cursor.description]
            return [dict(zip(columns, row)) for row in cursor.fetchall()]
