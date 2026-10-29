import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

FILES = {
    "config/__init__.py": "",
    "config/asgi.py": (
        "import os\n"
        "from django.core.asgi import get_asgi_application\n"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')\n"
        "application = get_asgi_application()\n"
    ),
    "config/wsgi.py": (
        "import os\n"
        "from django.core.wsgi import get_wsgi_application\n"
        "os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')\n"
        "application = get_wsgi_application()\n"
    ),
    "config/urls.py": (
        "from django.contrib import admin\n"
        "from django.urls import path, include\n\n"
        "urlpatterns = [\n"
        "    path('admin/', admin.site.urls),\n"
        "    path('', include('dashboard.urls')),\n"
        "    path('accounts/', include('accounts.urls')),\n"
        "    path('organization/', include('organization.urls')),\n"
        "    path('employees/', include('employees.urls')),\n"
        "    path('attendance/', include('attendance.urls')),\n"
        "    path('audit/', include('audit.urls')),\n"
        "    path('api/v1/', include('api.v1.urls')),\n"
        "]\n"
    ),
    "dashboard/__init__.py": "",
    "dashboard/urls.py": (
        "from django.urls import path\n"
        "from dashboard import views\n\n"
        "urlpatterns = [\n"
        "    path('', views.index, name='dashboard_home'),\n"
        "    path('dashboard/', views.index, name='dashboard_index'),\n"
        "]\n"
    ),
    "dashboard/views.py": (
        "from django.shortcuts import render\n\n"
        "def index(request):\n"
        "    context = {\n"
        "        'active_employees': 5240,\n"
        "        'present_today': 4982,\n"
        "        'absent_today': 128,\n"
        "        'leave_today': 130,\n"
        "        'pending_approvals': 14,\n"
        "    }\n"
        "    return render(request, 'dashboard/index.html', context)\n"
    ),
    "accounts/__init__.py": "",
    "accounts/urls.py": (
        "from django.urls import path\n"
        "from accounts import views\n\n"
        "urlpatterns = [\n"
        "    path('login/', views.EnterpriseLoginView.as_view(), name='login'),\n"
        "    path('logout/', views.user_logout, name='logout'),\n"
        "]\n"
    ),
    "accounts/views.py": (
        "from django.contrib.auth import logout\n"
        "from django.contrib.auth.views import LoginView\n"
        "from django.shortcuts import redirect\n"
        "from django.urls import reverse_lazy\n\n"
        "class EnterpriseLoginView(LoginView):\n"
        "    template_name = 'accounts/login.html'\n"
        "    redirect_authenticated_user = True\n"
        "    def get_success_url(self):\n"
        "        return reverse_lazy('dashboard_home')\n\n"
        "def user_logout(request):\n"
        "    logout(request)\n"
        "    return redirect('login')\n"
    ),
    "organization/__init__.py": "",
    "organization/urls.py": (
        "from django.urls import path\n\n"
        "urlpatterns = []\n"
    ),
    "employees/__init__.py": "",
    "employees/urls.py": (
        "from django.urls import path\n"
        "from employees import views\n\n"
        "urlpatterns = [\n"
        "    path('', views.employee_list, name='employee_list'),\n"
        "    path('<int:emp_key>/', views.employee_profile, name='employee_profile'),\n"
        "]\n"
    ),
    "employees/views.py": (
        "from django.shortcuts import render, get_object_or_404\n"
        "from django.core.paginator import Paginator\n"
        "from django.db.models import Q\n"
        "from employees.models import EmployeeInfoDetails, EmployeeExtendedProfile, DigitalServiceBook\n"
        "from documents.models import EmployeeDocument\n\n"
        "def employee_list(request):\n"
        "    search_query = request.GET.get('q', '').strip()\n"
        "    status_filter = request.GET.get('status', 'Active')\n"
        "    employees = EmployeeInfoDetails.objects.all()\n"
        "    if status_filter:\n"
        "        employees = employees.filter(EmployeeStatus=status_filter)\n"
        "    if search_query:\n"
        "        employees = employees.filter(\n"
        "            Q(EmpCode__icontains=search_query) |\n"
        "            Q(EmpName__icontains=search_query) |\n"
        "            Q(NID__icontains=search_query) |\n"
        "            Q(Mobile__icontains=search_query)\n"
        "        )\n"
        "    paginator = Paginator(employees.order_by('EmpCode'), 25)\n"
        "    page_obj = paginator.get_page(request.GET.get('page', 1))\n"
        "    return render(request, 'employees/employee_list.html', {'page_obj': page_obj, 'search_query': search_query, 'status_filter': status_filter})\n\n"
        "def employee_profile(request, emp_key):\n"
        "    employee = get_object_or_404(EmployeeInfoDetails, EmpKey=emp_key)\n"
        "    profile, _ = EmployeeExtendedProfile.objects.get_or_create(EmpKey=emp_key)\n"
        "    service_records = DigitalServiceBook.objects.filter(EmpKey=emp_key).order_by('-EffectiveDate')\n"
        "    documents = EmployeeDocument.objects.filter(EmpKey=emp_key).select_related('DocType')\n"
        "    return render(request, 'employees/employee_profile.html', {'emp': employee, 'profile': profile, 'service_records': service_records, 'documents': documents})\n"
    ),
    "attendance/__init__.py": "",
    "attendance/urls.py": (
        "from django.urls import path\n"
        "from attendance import views\n\n"
        "urlpatterns = [\n"
        "    path('', views.attendance_query_console, name='attendance_query_console'),\n"
        "]\n"
    ),
    "attendance/views.py": (
        "from django.shortcuts import render\n\n"
        "def attendance_query_console(request):\n"
        "    return render(request, 'attendance/query_console.html', {})\n"
    ),
    "audit/__init__.py": "",
    "audit/urls.py": (
        "from django.urls import path\n\n"
        "urlpatterns = []\n"
    ),
    "api/__init__.py": "",
    "api/v1/__init__.py": "",
    "api/v1/urls.py": (
        "from django.urls import path\n\n"
        "urlpatterns = []\n"
    ),
    "period_lock/__init__.py": "",
    "period_lock/middleware/period_lock_middleware.py": (
        "class PeriodLockMiddleware:\n"
        "    def __init__(self, get_response):\n"
        "        self.get_response = get_response\n"
        "    def __call__(self, request):\n"
        "        return self.get_response(request)\n"
    ),
}

for filepath, content in FILES.items():
    full_path = BASE_DIR / filepath
    full_path.parent.mkdir(parents=True, exist_ok=True)
    full_path.write_text(content, encoding="utf-8")
    print(f"Created: {filepath}")

print("\n>>> ALL PROJECT ROUTING & MODULE FILES GENERATED SUCCESSFULLY <<<")