from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.i18n import set_language
from . import views

urlpatterns = [
    # Root UI -> go to admin login
    path('', views.index, name='index'),

    # Language switching (Django's built-in view)
    path('i18n/setlang/', set_language, name='set_language'),

    # Public management endpoints are disabled and redirect to admin login
    path('groups/', views.redirect_admin_login, name='manage_groups'),
    path('users/', views.redirect_admin_login, name='manage_users'),
    path('surveys/', views.redirect_admin_login, name='manage_surveys'),
    path('surveys/<int:survey_id>/questions/add/', views.redirect_admin_login, name='add_question'),

    # Auth - public /login redirected to admin login to enforce single entrypoint
    path('login/', views.redirect_admin_login, name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='admin_login'), name='logout'),

    # survey taking and admin-styled user survey dashboard remain available for authenticated users
    path('surveys/<int:survey_id>/take/', views.take_survey, name='take_survey'),
    path('admin-surveys/', views.admin_user_surveys, name='admin_user_surveys'),
    path('surveys/<int:survey_id>/results/', views.survey_results, name='survey_results'),

    # API: keep the questions_for_user API (requires authentication or username param)
    path('api/questions_for_user/', views.questions_for_user, name='questions_for_user_root'),
    path('api/questions_for_user/<str:username>/', views.questions_for_user, name='questions_for_user'),
]
