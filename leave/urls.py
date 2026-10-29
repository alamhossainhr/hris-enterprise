from django.urls import path
from leave import views

urlpatterns = [
    path("", views.leave_dashboard, name="leave_dashboard"),
    path("apply/", views.apply_leave, name="apply_leave"),
    path("earn-leave/compute/", views.compute_earn_leave_view, name="compute_earn_leave"),
    path("maternity/", views.maternity_benefit_list, name="maternity_benefit_list"),
]
