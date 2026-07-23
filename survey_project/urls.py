from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect

# Redirect the admin's Add User URL to the simplified public users UI so the
# add experience is identical and avoids admin template incompatibilities.
def _redirect_admin_add_user(request):
    return redirect('manage_users')

urlpatterns = [
    path('admin/auth/user/add/', _redirect_admin_add_user),
    path('admin/', admin.site.urls),
    path('', include('surveys.urls')),
]
