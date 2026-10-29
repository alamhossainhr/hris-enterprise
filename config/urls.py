from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("dashboard.urls")),
    path("accounts/", include("accounts.urls")),
    path("organization/", include("organization.urls")),
    path("employees/", include("employees.urls")),
    path("shifts/", include("shifts.urls")),
    path("attendance/", include("attendance.urls")),
    path("leave/", include("leave.urls")),
    path("audit/", include("audit.urls")),
    path("api/v1/", include("api.v1.urls")),
]
