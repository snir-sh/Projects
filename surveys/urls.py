from django.urls import path
from . import views

urlpatterns = [
    # Supports URL parameter and query param / authentication fallback
    path('api/questions_for_user/', views.questions_for_user, name='questions_for_user_root'),
    path('api/questions_for_user/<str:username>/', views.questions_for_user, name='questions_for_user'),
]
