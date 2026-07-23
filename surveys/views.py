from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

from .models import Question, UserType, UserTypeAssignment, Survey


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


# --- Simple web UI views ---

from django.shortcuts import redirect


def index(request):
    """Redirect root to the login page (nice UI provided at /login/)."""
    return redirect('login')


def manage_groups(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            UserType.objects.get_or_create(name=name)
        return HttpResponseRedirect(reverse('manage_groups'))

    groups = UserType.objects.all().order_by('name')
    return render(request, 'surveys/groups.html', {'groups': groups})


def manage_users(request):
    User = get_user_model()
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        selected = request.POST.getlist('groups')
        if username:
            user, created = User.objects.get_or_create(username=username)
            # set default password if newly created or to reset
            if created:
                user.set_password('password')
                user.email = ''
                user.save()
            # clear existing assignments and set new ones
            UserTypeAssignment.objects.filter(user=user).delete()
            for gid in selected:
                try:
                    ut = UserType.objects.get(id=int(gid))
                    UserTypeAssignment.objects.get_or_create(user=user, user_type=ut)
                except Exception:
                    continue
        return HttpResponseRedirect(reverse('manage_users'))

    groups = UserType.objects.all().order_by('name')
    User = get_user_model()
    users = User.objects.exclude(is_superuser=True).order_by('username')
    # gather assignments
    user_map = []
    for u in users:
        uts = [a.user_type.name for a in u.user_type_assignments.select_related('user_type')]
        user_map.append((u, uts))
    return render(request, 'surveys/users.html', {'groups': groups, 'users': user_map})
