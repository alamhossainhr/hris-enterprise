from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy

class EnterpriseLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    def get_success_url(self):
        return reverse_lazy('dashboard_home')

def user_logout(request):
    logout(request)
    return redirect('login')
