from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', views.EnterpriseLoginView.as_view(), name='login'),
    path('logout/', views.user_logout, name='logout'),
]
