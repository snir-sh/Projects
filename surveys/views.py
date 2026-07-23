from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import Question


def questions_for_user(request, username=None):
    """Return JSON list of questions visible to a user.

    Username resolution order:
    1. URL parameter (username)
    2. GET query parameter (?username=)
    3. Authenticated request.user

    If no username can be determined, return 400.
    Visibility rules:
    - Questions with no user_types are common and visible to everyone.
    - Questions assigned to any UserType the user belongs to are visible to that user.
    """
    User = get_user_model()

    if username is None:
        username = request.GET.get('username')
    if username is None and hasattr(request, 'user') and request.user.is_authenticated:
        username = request.user.username

    if username is None:
        return JsonResponse({'error': 'username required (provide in URL or ?username= or authenticate)'}, status=400)

    user = get_object_or_404(User, username=username)

    user_type_ids = list(user.user_type_assignments.values_list('user_type', flat=True))

    qs = Question.objects.filter(Q(user_types__isnull=True) | Q(user_types__in=user_type_ids)).distinct()

    data = []
    for q in qs:
        data.append({
            'id': q.id,
            'text': q.text,
            'question_type': q.question_type,
            'required': q.required,
            'surveys': [s.title for s in q.surveys.all()],
            'user_types': [ut.name for ut in q.user_types.all()],
        })

    return JsonResponse(data, safe=False)
