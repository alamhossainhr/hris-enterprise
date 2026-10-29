import re
from datetime import date, datetime, timedelta
from django.core.cache import cache
from django.db import connection


class AttendanceTableService:
    TABLE_PATTERN = re.compile(r"^\d{4}(1[0-2]|[1-9])$")

    @classmethod
    def get_table_name(cls, target_date: date) -> str:
        """Resolves date to YYYYM format without leading zeros (e.g., 2026-08-20 -> '20268')."""
        return f"{target_date.year}{target_date.month}"

    @classmethod
    def validate_table_name(cls, table_name: str) -> bool:
        """Validates format and range to prevent SQL injection and errors."""
        name_str = str(table_name).strip()
        if not cls.TABLE_PATTERN.match(name_str):
            raise ValueError(f"Security/Integrity Error: Invalid attendance table name '{table_name}'")
        
        year = int(name_str[:4])
        month = int(name_str[4:])
        if not (2000 <= year <= 2100 and 1 <= month <= 12):
            raise ValueError(f"Attendance year/month out of enterprise boundaries: {year}-{month}")
        return True

    @classmethod
    def get_tables_between_dates(cls, from_date: date, to_date: date) -> list[dict]:
        """
        Calculates all intermediate YYYYM table intervals.
        Example: 2026-07-25 to 2026-08-20 ->
        [
            {'table': '20267', 'start': '2026-07-25', 'end': '2026-07-31'},
            {'table': '20268', 'start': '2026-08-01', 'end': '2026-08-20'}
        ]
        """
        if from_date > to_date:
            raise ValueError(f"from_date ({from_date}) cannot be greater than to_date ({to_date})")

        intervals = []
        cur_year, cur_month = from_date.year, from_date.month
        end_year, end_month = to_date.year, to_date.month

        while (cur_year, cur_month) <= (end_year, end_month):
            table_name = f"{cur_year}{cur_month}"
            cls.validate_table_name(table_name)

            month_start = date(cur_year, cur_month, 1)
            # Find next month start then subtract one day for accurate end-of-month
            if cur_month == 12:
                next_month_start = date(cur_year + 1, 1, 1)
            else:
                next_month_start = date(cur_year, cur_month + 1, 1)
            month_end = next_month_start - timedelta(days=1)

            range_start = max(from_date, month_start)
            range_end = min(to_date, month_end)

            intervals.append({
                "table": table_name,
                "start": range_start.strftime("%Y-%m-%d"),
                "end": range_end.strftime("%Y-%m-%d"),
            })

            if cur_month == 12:
                cur_year += 1
                cur_month = 1
            else:
                cur_month += 1

        return intervals

    @classmethod
    def table_exists(cls, table_name: str) -> bool:
        cls.validate_table_name(table_name)
        cache_key = f"att_tbl_exists_{table_name}"
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = %s AND TABLE_SCHEMA = 'dbo'
            """, [table_name])
            exists = cursor.fetchone()[0] > 0
            cache.set(cache_key, exists, timeout=3600)
            return exists

    @classmethod
    def create_monthly_attendance_table(cls, year: int, month: int, base_template_table: str = "20268") -> None:
        """Provisions a new monthly attendance table by replicating schema and creating clustered/non-clustered indexes."""
        table_name = f"{year}{month}"
        cls.validate_table_name(table_name)

        if cls.table_exists(table_name):
            return

        with connection.cursor() as cursor:
            # Clone schema structure
            cursor.execute(f"SELECT TOP 0 * INTO [{table_name}] FROM [{base_template_table}];")
            
            # Apply Primary Key and Performance Indexes
            cursor.execute(f"""
                ALTER TABLE [{table_name}] ALTER COLUMN AttKey BIGINT NOT NULL;
                ALTER TABLE [{table_name}] ADD CONSTRAINT PK_{table_name}_AttKey PRIMARY KEY CLUSTERED (AttKey);
                CREATE NONCLUSTERED INDEX IX_{table_name}_EmpKey_WorkDate ON [{table_name}](EmpKey, WorkDate);
                CREATE NONCLUSTERED INDEX IX_{table_name}_WorkDate_DayStatus ON [{table_name}](WorkDate, DayStatus);
            """)
            
        cache.set(f"att_tbl_exists_{table_name}", True, timeout=86400)