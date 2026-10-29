from django.urls import path
from shifts import views

urlpatterns = [
    path('', views.shift_list, name='shift_list'),
    path('add/', views.shift_create, name='shift_create'),
]
