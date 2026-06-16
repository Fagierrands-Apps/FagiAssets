from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def discovery_dashboard(request):
    """Network discovery dashboard"""
    context = {
        'title': 'Network Discovery',
        'message': 'Network discovery functionality will be implemented here.'
    }
    return render(request, 'discovery/dashboard.html', context)
