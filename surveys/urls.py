from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root UI (redirects to login)
    path('', views.index, name='index'),
    path('groups/', views.manage_groups, name='manage_groups'),
    path('users/', views.manage_users, name='manage_users'),
    path('surveys/', views.manage_surveys, name='manage_surveys'),
    path('surveys/<int:survey_id>/questions/add/', views.add_question, name='add_question'),

    # Auth
    path('login/', auth_views.LoginView.as_view(template_name='surveys/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # API: supports URL parameter and query param / authentication fallback
    path('api/questions_for_user/', views.questions_for_user, name='questions_for_user_root'),
    path('api/questions_for_user/<str:username>/', views.questions_for_user, name='questions_for_user'),
]
