from django.urls import path
from employees import views

urlpatterns = [
    path('', views.employee_list, name='employee_list'),
    path('<int:emp_key>/', views.employee_profile, name='employee_profile'),
    path('<int:emp_key>/edit/', views.employee_profile_edit, name='employee_profile_edit'),
    path('<int:emp_key>/event/add/', views.add_service_event, name='add_service_event'),
    path('<int:emp_key>/documents/upload/', views.upload_document, name='upload_document'),
]
