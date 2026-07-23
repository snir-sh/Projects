from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse

from .models import Question, Survey
from django.contrib.auth.models import Group


def questions_for_user(request, username=None):
    """Return JSON list of questions visible to a user.

    Username resolution order:
    1. URL parameter (username)
    2. GET query parameter (?username=)
    3. Authenticated request.user

    If no username can be determined, return 400.
    Visibility rules:
    - Questions with no groups are common and visible to everyone.
    - Questions assigned to any Group the user belongs to are visible to that user.
    """
    User = get_user_model()

    if username is None:
        username = request.GET.get('username')
    if username is None and hasattr(request, 'user') and request.user.is_authenticated:
        username = request.user.username

    if username is None:
        return JsonResponse({'error': 'username required (provide in URL or ?username= or authenticate)'}, status=400)

    user = get_object_or_404(User, username=username)

    # gather group ids for the user
    user_group_ids = list(user.groups.values_list('id', flat=True))

    qs = Question.objects.filter(Q(groups__isnull=True) | Q(groups__in=user_group_ids)).distinct()

    data = []
    for q in qs:
        data.append({
            'id': q.id,
            'text': q.text,
            'question_type': q.question_type,
            'required': q.required,
            'survey': q.survey.title if q.survey else None,
            'groups': [g.name for g in q.groups.all()],
        })

    return JsonResponse(data, safe=False)


# --- Simple web UI views ---

from django.shortcuts import redirect


def index(request):
    """Redirect root to the login page (nice UI provided at /login/)."""
    return redirect('login')


def manage_groups(request):
    # Manage Django auth Groups
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            Group.objects.get_or_create(name=name)
        if '_addanother' in request.POST:
            return HttpResponseRedirect(reverse('manage_groups'))
        return HttpResponseRedirect(reverse('index'))

    groups = Group.objects.all().order_by('name')
    return render(request, 'surveys/groups.html', {'groups': groups})


def manage_users(request):
    User = get_user_model()
    error = None
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        selected = request.POST.get('group')  # single group selection
        if not username:
            error = 'Username is required.'
        else:
            user, created = User.objects.get_or_create(username=username)
            if created:
                user.set_password('password')
                user.email = ''
                user.save()
            # assign single group
            try:
                if selected and selected.isdigit():
                    g = Group.objects.get(id=int(selected))
                    user.groups.set([g])
                else:
                    user.groups.clear()
            except Exception:
                pass
        if error:
            groups = Group.objects.all().order_by('name')
            users = User.objects.exclude(is_superuser=True).order_by('username')
            user_map = []
            for u in users:
                gnames = [g.name for g in u.groups.all()]
                user_map.append((u, gnames))
            return render(request, 'surveys/users.html', {'groups': groups, 'users': user_map, 'error': error, 'presel': int(selected) if selected and selected.isdigit() else None})

        if '_addanother' in request.POST:
            return HttpResponseRedirect(reverse('manage_users'))
        return HttpResponseRedirect(reverse('index'))

    groups = Group.objects.all().order_by('name')
    User = get_user_model()
    users = User.objects.exclude(is_superuser=True).order_by('username')
    user_map = []
    for u in users:
        gnames = [g.name for g in u.groups.all()]
        user_map.append((u, gnames))
    return render(request, 'surveys/users.html', {'groups': groups, 'users': user_map})
