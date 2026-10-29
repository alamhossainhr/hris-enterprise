from django.urls import path
from dashboard import views

urlpatterns = [
    path('', views.index, name='dashboard_home'),
    path('dashboard/', views.index, name='dashboard_index'),
]
