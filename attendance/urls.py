from django.urls import path
from attendance import views

urlpatterns = [
    path('', views.attendance_query_console, name='attendance_query_console'),
    path('process/', views.attendance_process_view, name='attendance_process'),
    path('punch/add/', views.raw_punch_manual, name='raw_punch_manual'),
]
