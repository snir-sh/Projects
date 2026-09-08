from django.shortcuts import redirect
from django.urls import reverse


class NonStaffAdminRedirectMiddleware:
    """Redirect non-staff users from /admin/ to /admin-surveys/."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check if user is authenticated and non-staff accessing /admin/
        if (request.path.startswith('/admin/') and 
            request.user.is_authenticated and 
            not request.user.is_staff):
            return redirect(reverse('admin_user_surveys'))
        
        response = self.get_response(request)
        return response
