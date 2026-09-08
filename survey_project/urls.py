from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from surveys.views import AdminLoginView, admin_user_surveys

# Redirect admin login to custom login view (no staff requirement)
admin.site.login_url = 'admin_login'
admin.site.index_title = 'לוח בקרה'

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/', admin.site.urls),
    path('admin-surveys/', admin_user_surveys, name='admin_user_surveys'),
    path('', include('surveys.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
