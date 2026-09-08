from django.http import JsonResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.utils.translation import gettext_lazy as _

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
            choice_images_text = request.POST.get('choice_images', '').strip()
            max_sel = int(request.POST.get('max_selections') or 3)
            multi_count = int(request.POST.get('multi_text_count') or 3)
            q = Question.objects.create(
                text=text,
                question_type=qtype,
                choices=choices_text,
                choice_images=choice_images_text,
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
    """Login view for users—superuser goes to admin, regular users see surveys."""
    template_name = 'admin/login.html'

    def get_success_url(self):
        user = getattr(self.request, 'user', None)
        if user and user.is_superuser:
            return reverse('admin:index')
        return reverse('admin_user_surveys')


@login_required
def admin_user_surveys(request):
    """Show all surveys to all authenticated users. Questions will be filtered per-question based on user groups."""
    user = request.user
    
    # Show ALL surveys to all users - questions are filtered per-question in take_survey
    surveys = Survey.objects.all()
    
    # Add completion status for each survey
    survey_list = []
    for survey in surveys:
        latest_response = Response.objects.filter(
            survey=survey,
            user_identifier=user.username,
        ).order_by('-updated_at', '-submitted_at', '-id').first()
        
        survey_list.append({
            'survey': survey,
            'completed': latest_response.status == Response.COMPLETED if latest_response else False,
            'draft': latest_response if latest_response and latest_response.status == Response.DRAFT else None,
        })
    
    return render(request, 'surveys/admin_user_surveys.html', {'survey_list': survey_list})


@login_required
def take_survey(request, survey_id):
    """Allow a logged-in user to take a survey; only shows questions visible to their groups.
    Supports draft saves and resuming incomplete surveys."""
    user = request.user
    survey = get_object_or_404(Survey, pk=survey_id)
    user_group_ids = list(user.groups.values_list('id', flat=True))
    qs = Question.objects.filter(Q(survey=survey)).filter(Q(groups__isnull=True) | Q(groups__in=user_group_ids)).distinct()
    
    # Load the latest response so users can review/edit their latest submitted answers too.
    resp = Response.objects.filter(
        survey=survey,
        user_identifier=user.username,
    ).order_by('-updated_at', '-submitted_at', '-id').first()
    
    if request.method == 'POST':
        # Create or update response
        if not resp:
            resp = Response.objects.create(survey=survey, user_identifier=user.username, status=Response.DRAFT)
        else:
            # Clear previous answers for this response
            resp.answers.all().delete()
        
        # Save answers
        for q in qs:
            if q.question_type == Question.CHOICE:
                key = f'question_{q.id}'
                val = request.POST.get(key, '').strip()
                Answer.objects.create(response=resp, question=q, answer_text=val)
            elif q.question_type == Question.MULTI_SELECT:
                key = f'question_{q.id}'
                vals = request.POST.getlist(key)
                ordered_vals = []
                raw_order = request.POST.get(f'{key}__order', '').strip()
                if raw_order:
                    try:
                        parsed_order = json.loads(raw_order)
                        if isinstance(parsed_order, list):
                            ordered_vals = [value for value in parsed_order if value in vals]
                    except (TypeError, ValueError):
                        ordered_vals = []

                if ordered_vals:
                    vals = ordered_vals + [value for value in vals if value not in ordered_vals]
                try:
                    vals = vals[:int(q.max_selections)]
                except Exception:
                    pass
                Answer.objects.create(response=resp, question=q, answer_text=json.dumps(vals))
            elif q.question_type == Question.MULTI_TEXT:
                parts = []
                for i in range(1, q.multi_text_count + 1):
                    parts.append(request.POST.get(f'question_{q.id}_{i}', '').strip())
                Answer.objects.create(response=resp, question=q, answer_text=json.dumps(parts))
            else:
                key = f'question_{q.id}'
                val = request.POST.get(key, '').strip()
                Answer.objects.create(response=resp, question=q, answer_text=val)
        
        # Check if submit button was clicked
        if 'submit' in request.POST:
            resp.status = Response.COMPLETED
            resp.save()
            messages.success(request, _('Survey submitted successfully!'))
            return render(request, 'surveys/take_survey_submitted.html', {'survey': survey})
        else:
            resp.status = Response.DRAFT
            resp.save()
            messages.info(request, _('Survey draft saved.'))
            return redirect('take_survey', survey_id=survey_id)

    # Prepare question structures for the template
    questions = []
    for q in qs:
        option_items = q.get_option_items()
        opts = [item['label'] for item in option_items]
        indices = list(range(1, q.multi_text_count + 1))
        
        # Load existing answer if resuming a draft
        existing_answer = None
        if resp:
            existing_answer = resp.answers.filter(question=q).first()
        
        existing_multi_text_answers = []
        if existing_answer and q.question_type == Question.MULTI_TEXT:
            try:
                parsed_existing_answer = json.loads(existing_answer.answer_text)
                if isinstance(parsed_existing_answer, list):
                    existing_multi_text_answers = parsed_existing_answer
            except (TypeError, ValueError):
                existing_multi_text_answers = []

        multi_text_values = [
            {
                'index': idx,
                'value': existing_multi_text_answers[idx - 1] if idx - 1 < len(existing_multi_text_answers) else '',
            }
            for idx in indices
        ]

        questions.append({
            'id': q.id,
            'text': q.text,
            'type': q.question_type,
            'required': q.required,
            'options': opts,
            'option_items': option_items,
            'max_selections': q.max_selections,
            'multi_text_count': q.multi_text_count,
            'multi_text_indices': indices,
            'multi_text_values': multi_text_values,
            'existing_answer': existing_answer.answer_text if existing_answer else None,
            'existing_multi_text_answers': existing_multi_text_answers,
        })
    
    return render(request, 'surveys/take_survey.html', {
        'survey': survey,
        'questions': questions,
        'is_draft': resp is not None and resp.status == Response.DRAFT,
    })


# --- Survey Results Dashboard for Staff ---
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Q
import json

@staff_member_required
def survey_results(request, survey_id):
    """Display aggregated results for a survey (staff/admin only)."""
    survey = get_object_or_404(Survey, id=survey_id)
    
    # Get all responses (both completed and draft)
    responses = survey.responses.all()
    total_responses = responses.count()
    
    if total_responses == 0:
        questions_data = []
    else:
        questions_data = []
        
        for question in survey.questions.all():
            q_data = {
                'id': question.id,
                'text': question.text,
                'type': question.question_type,
            }
            
            if question.question_type == Question.CHOICE:
                # Get all answers for this choice question
                answers = Answer.objects.filter(question=question, response__survey=survey)
                choice_counts = {}
                option_items = question.get_option_items()
                 
                # Initialize with all options
                for item in option_items:
                    choice_counts[item['label']] = 0
                 
                # Count answers
                for answer in answers:
                    if answer.answer_text:
                        choice_counts[answer.answer_text] = choice_counts.get(answer.answer_text, 0) + 1
                 
                q_data['results'] = []
                option_image_map = {item['label']: item['image_url'] for item in option_items}
                for option, count in choice_counts.items():
                    percentage = (count / total_responses * 100) if total_responses > 0 else 0
                    q_data['results'].append({
                        'option': option,
                        'image_url': option_image_map.get(option, ''),
                        'count': count,
                        'percentage': round(percentage, 1),
                    })
            
            elif question.question_type == Question.MULTI_SELECT:
                # Get all multi-select answers with weighted scoring
                answers = Answer.objects.filter(question=question, response__survey=survey)
                option_scores = {}
                option_items = question.get_option_items()
                 
                # Initialize with all options
                for item in option_items:
                    option_scores[item['label']] = 0
                 
                # Calculate weighted scores based on selection order
                # Logic: if 3 selections -> 3,2,1 points; if 1-2 selections -> all get 1 point
                for answer in answers:
                    if answer.answer_text:
                        try:
                            selected = json.loads(answer.answer_text)
                            num_selections = len(selected)
                            
                            for position, option in enumerate(selected):
                                if num_selections == 3:
                                    # Weighted: 3, 2, 1
                                    points = 3 - position
                                else:
                                    # All get 1 point for 1 or 2 selections
                                    points = 1
                                
                                option_scores[option] = option_scores.get(option, 0) + points
                        except (json.JSONDecodeError, ValueError):
                            pass
                 
                q_data['results'] = []
                option_image_map = {item['label']: item['image_url'] for item in option_items}
                for option, score in option_scores.items():
                    q_data['results'].append({
                        'option': option,
                        'image_url': option_image_map.get(option, ''),
                        'score': score,
                    })
            
            elif question.question_type == Question.TEXT:
                # Get all text answers
                answers = Answer.objects.filter(question=question, response__survey=survey).values_list('answer_text', flat=True)
                q_data['results'] = [{'text': a} for a in answers if a]
            
            elif question.question_type == Question.MULTI_TEXT:
                # Get all multi-text answers with weighted scoring by answer order.
                answers = Answer.objects.filter(question=question, response__survey=survey).values_list('answer_text', flat=True)
                q_data['results'] = []
                for answer in answers:
                    if answer:
                        try:
                            texts = json.loads(answer)
                            filled_texts = [t for t in texts if t]
                            total_filled = len(filled_texts)
                            for position, text in enumerate(filled_texts):
                                if total_filled == 3:
                                    points = 3 - position
                                else:
                                    points = 1
                                q_data['results'].append({'text': text, 'score': points})
                        except (json.JSONDecodeError, ValueError):
                            q_data['results'].append({'text': answer, 'score': 1})
            
            questions_data.append(q_data)
    
    return render(request, 'surveys/survey_results.html', {
        'survey': survey,
        'total_responses': total_responses,
        'questions_data': questions_data,
    })
