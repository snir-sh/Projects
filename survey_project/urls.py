from django.contrib import admin
from django.urls import path, include
from surveys.views import AdminLoginView, admin_user_surveys

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin-surveys/', admin_user_surveys, name='admin_user_surveys'),
    path('', include('surveys.urls')),
]
