from django.urls import path
from organization import views

urlpatterns = [
    path('', views.org_tree, name='org_tree'),
    path('company/add/', views.company_create, name='company_create'),
    path('department/add/', views.department_create, name='department_create'),
    path('designation/add/', views.designation_create, name='designation_create'),
]
