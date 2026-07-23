from django.urls import path
from . import views

urlpatterns = [
    # Root UI
    path('', views.index, name='index'),
    path('groups/', views.manage_groups, name='manage_groups'),
    path('users/', views.manage_users, name='manage_users'),

    # API: supports URL parameter and query param / authentication fallback
    path('api/questions_for_user/', views.questions_for_user, name='questions_for_user_root'),
    path('api/questions_for_user/<str:username>/', views.questions_for_user, name='questions_for_user'),
]
