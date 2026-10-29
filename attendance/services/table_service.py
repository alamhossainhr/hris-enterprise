import re
from datetime import date, timedelta
from django.core.cache import cache
from django.db import connection

class AttendanceTableService:
    TABLE_PATTERN = re.compile(r"^\d{4}(1[0-2]|[1-9])$")

    @classmethod
    def get_table_name(cls, target_date: date) -> str:
        return f"{target_date.year}{target_date.month}"

    @classmethod
    def validate_table_name(cls, table_name: str) -> bool:
        name_str = str(table_name).strip()
        if not cls.TABLE_PATTERN.match(name_str):
            raise ValueError(f"Invalid attendance table name '{table_name}'")
        year = int(name_str[:4])
        month = int(name_str[4:])
        if not (2000 <= year <= 2100 and 1 <= month <= 12):
            raise ValueError(f"Attendance year/month out of range: {year}-{month}")
        return True

    @classmethod
    def get_tables_between_dates(cls, from_date: date, to_date: date) -> list[dict]:
        if from_date > to_date:
            raise ValueError(f"from_date ({from_date}) cannot be greater than to_date ({to_date})")
        intervals = []
        cur_year, cur_month = from_date.year, from_date.month
        end_year, end_month = to_date.year, to_date.month
        while (cur_year, cur_month) <= (end_year, end_month):
            table_name = f"{cur_year}{cur_month}"
            cls.validate_table_name(table_name)
            month_start = date(cur_year, cur_month, 1)
            next_month_start = date(cur_year + 1, 1, 1) if cur_month == 12 else date(cur_year, cur_month + 1, 1)
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
    def create_monthly_attendance_table(cls, year: int, month: int) -> None:
        table_name = f"{year}{month}"
        cls.validate_table_name(table_name)
        if cls.table_exists(table_name):
            return
        with connection.cursor() as cursor:
            cursor.execute(f"""
                CREATE TABLE [{table_name}] (
                    AttKey BIGINT NOT NULL PRIMARY KEY CLUSTERED,
                    EmpKey BIGINT NOT NULL,
                    WorkDate DATE NOT NULL,
                    ShiftID BIGINT NULL,
                    InTime TIME(0) NULL,
                    OutTime TIME(0) NULL,
                    DayStatus VARCHAR(10) NOT NULL,
                    LateMinute INT DEFAULT 0,
                    EarlyExitMinute INT DEFAULT 0,
                    PayHour DECIMAL(5,2) DEFAULT 8.0,
                    OTHour DECIMAL(5,2) DEFAULT 0.0,
                    EOT DECIMAL(5,2) DEFAULT 0.0,
                    NightDays INT DEFAULT 0,
                    TiffinDay INT DEFAULT 0,
                    IftarDay INT DEFAULT 0,
                    Remarks NVARCHAR(255) NULL,
                    DateAdded DATETIME DEFAULT GETDATE(),
                    AddedBy NVARCHAR(100) NULL,
                    DateUpdated DATETIME NULL,
                    UpdatedBy NVARCHAR(100) NULL
                );
                CREATE NONCLUSTERED INDEX IX_{table_name}_EmpKey_WorkDate ON [{table_name}](EmpKey, WorkDate);
                CREATE NONCLUSTERED INDEX IX_{table_name}_WorkDate_DayStatus ON [{table_name}](WorkDate, DayStatus);
            """)
        cache.set(f"att_tbl_exists_{table_name}", True, timeout=86400)
