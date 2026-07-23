from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView

from .models import Question, Survey, Response, Answer
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
    """Redirect root to the admin login page."""
    return redirect('admin_login')


def redirect_admin_login(request):
    """Redirect helper to send public routes to admin login."""
    return redirect('admin_login')


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
                from django.conf import settings as _settings
                user.set_password(getattr(_settings, 'DEFAULT_USER_PASSWORD', 'password'))
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


# --- Surveys & Questions public UI ---

def manage_surveys(request):
    """List surveys and allow creating a new Survey."""
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        if title:
            Survey.objects.get_or_create(title=title, defaults={'description': description})
            if '_addanother' in request.POST:
                return HttpResponseRedirect(reverse('manage_surveys'))
            return HttpResponseRedirect(reverse('manage_surveys'))

    surveys = Survey.objects.all().order_by('-created_at')
    return render(request, 'surveys/surveys.html', {'surveys': surveys})


def add_question(request, survey_id):
    """Add a Question to a Survey. Questions can be common (no groups) or assigned to groups."""
    survey = get_object_or_404(Survey, pk=survey_id)
    groups = Group.objects.all().order_by('name')
    error = None
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        qtype = request.POST.get('question_type', 'text')
        required = bool(request.POST.get('required'))
        selected = request.POST.getlist('groups')
        if not text:
            error = 'Question text is required.'
        else:
            choices_text = request.POST.get('choices', '').strip()
            max_sel = int(request.POST.get('max_selections') or 3)
            multi_count = int(request.POST.get('multi_text_count') or 3)
            q = Question.objects.create(
                text=text,
                question_type=qtype,
                choices=choices_text,
                max_selections=max_sel,
                multi_text_count=multi_count,
                required=required,
                survey=survey
            )
            if selected:
                try:
                    q.groups.set([int(g) for g in selected if g.isdigit()])
                except Exception:
                    pass
            return HttpResponseRedirect(reverse('manage_surveys'))

    return render(request, 'surveys/add_question.html', {'survey': survey, 'groups': groups, 'error': error})


# --- Admin-facing simplified login and survey dashboard for non-staff users ---
class AdminLoginView(LoginView):
    """Use at /admin/login/ so non-staff users are redirected to their survey dashboard."""
    template_name = 'admin/login.html'

    def get_success_url(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_authenticated:
            if user.is_staff:
                return reverse('admin:index')
            return reverse('admin_user_surveys')
        return super().get_success_url()


@login_required
def admin_user_surveys(request):
    """Show surveys relevant to the logged-in user's groups. Intended for non-staff users logging in at /admin/login/."""
    user = request.user
    if user.is_staff:
        # staff should go to the normal admin index
        return redirect('admin:index')
    user_group_ids = list(user.groups.values_list('id', flat=True))
    # surveys that have questions assigned to any of the user's groups
    surveys = Survey.objects.filter(questions__groups__in=user_group_ids).distinct()
    # if no group-specific surveys, include surveys with common questions
    if not surveys.exists():
        surveys = Survey.objects.filter(questions__groups__isnull=True).distinct()
    return render(request, 'surveys/admin_user_surveys.html', {'surveys': surveys})


@login_required
def take_survey(request, survey_id):
    """Allow a logged-in user to take a survey; only shows questions visible to their groups."""
    user = request.user
    survey = get_object_or_404(Survey, pk=survey_id)
    user_group_ids = list(user.groups.values_list('id', flat=True))
    qs = Question.objects.filter(Q(survey=survey)).filter(Q(groups__isnull=True) | Q(groups__in=user_group_ids)).distinct()
    if request.method == 'POST':
        # create Response and Answers
        identifier = user.username
        resp = Response.objects.create(survey=survey, user_identifier=identifier)
        for q in qs:
            if q.question_type == Question.CHOICE:
                key = f'question_{q.id}'
                val = request.POST.get(key, '').strip()
                Answer.objects.create(response=resp, question=q, answer_text=val)
            elif q.question_type == Question.MULTI_SELECT:
                key = f'question_{q.id}'
                vals = request.POST.getlist(key)
                # trim to allowed max selections to be safe
                try:
                    vals = vals[:int(q.max_selections)]
                except Exception:
                    pass
                # store as JSON array string
                import json
                Answer.objects.create(response=resp, question=q, answer_text=json.dumps(vals))
            elif q.question_type == Question.MULTI_TEXT:
                parts = []
                for i in range(1, q.multi_text_count + 1):
                    parts.append(request.POST.get(f'question_{q.id}_{i}', '').strip())
                import json
                Answer.objects.create(response=resp, question=q, answer_text=json.dumps(parts))
            else:
                key = f'question_{q.id}'
                val = request.POST.get(key, '').strip()
                Answer.objects.create(response=resp, question=q, answer_text=val)
        return render(request, 'surveys/take_survey_submitted.html', {'survey': survey})

    # prepare question structures for the template
    questions = []
    for q in qs:
        opts = [o for o in (q.choices or '').splitlines() if o.strip()]
        indices = list(range(1, q.multi_text_count + 1))
        questions.append({'id': q.id, 'text': q.text, 'type': q.question_type, 'required': q.required, 'options': opts, 'max_selections': q.max_selections, 'multi_text_count': q.multi_text_count, 'multi_text_indices': indices})
    return render(request, 'surveys/take_survey.html', {'survey': survey, 'questions': questions})
