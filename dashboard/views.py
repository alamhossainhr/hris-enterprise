from django.shortcuts import render

def index(request):
    context = {
        'active_employees': 5240,
        'present_today': 4982,
        'absent_today': 128,
        'leave_today': 130,
        'pending_approvals': 14,
    }
    return render(request, 'dashboard/index.html', context)
