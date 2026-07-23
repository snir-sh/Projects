from django.contrib import admin
from django.urls import path, include
from surveys.views import AdminLoginView, admin_user_surveys

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    # Override admin login so non-staff users are sent to their survey dashboard
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    # A short landing route for non-staff users after admin login
    path('admin-surveys/', admin_user_surveys, name='admin_user_surveys'),
    # Admin and app urls
    path('admin/', admin.site.urls),
    path('', include('surveys.urls')),
]
