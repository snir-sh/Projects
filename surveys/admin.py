from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms.widgets import CheckboxSelectMultiple
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import Survey, Question, Response, Answer
from django.contrib.auth.models import Group
from django.conf import settings
import json
import csv


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    readonly_fields = ('question', 'formatted_answer')
    fields = ('question', 'formatted_answer')
    
    def formatted_answer(self, obj):
        """Format answer_text: parse JSON for multi-select/multi-text, display as comma-separated list."""
        answer_text = obj.answer_text
        if not answer_text:
            return '-'
        
        # Try to parse as JSON (for multi-select and multi-text)
        try:
            parsed = json.loads(answer_text)
            if isinstance(parsed, list):
                return ', '.join(str(item) for item in parsed)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Not JSON, return as-is (text or choice)
        return answer_text
    
    formatted_answer.short_description = 'Answer'


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'user_identifier', 'status_display', 'submitted_at')
    list_filter = ('survey', 'status', 'submitted_at')
    readonly_fields = ('survey', 'user_identifier', 'submitted_at', 'updated_at')
    fields = ('survey', 'user_identifier', 'status', 'submitted_at', 'updated_at')
    inlines = [AnswerInline]
    actions = ['export_as_csv']

    def status_display(self, obj):
        """Display status with color coding."""
        if obj.status == Response.COMPLETED:
            return format_html(
                '<span style="color: green; font-weight: bold;">✓ {}</span>',
                _('Completed')
            )
        else:  # DRAFT
            return format_html(
                '<span style="color: orange; font-weight: bold;">⏸ {}</span>',
                _('Draft')
            )
    status_display.short_description = _('Status')

    def export_as_csv(self, request, queryset):
        """Export selected responses to CSV with all answers."""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="survey_responses.csv"'
        
        writer = csv.writer(response)
        
        # Write header: Response ID, Survey, User, Submitted At, then dynamic question columns
        all_questions = Question.objects.order_by('id')
        header = ['Response ID', 'Survey', 'User', 'Submitted At']
        header.extend([q.text for q in all_questions])
        writer.writerow(header)
        
        # Write data rows
        for response_obj in queryset:
            row = [
                response_obj.id,
                response_obj.survey.title,
                response_obj.user_identifier,
                response_obj.submitted_at.strftime('%Y-%m-%d %H:%M:%S'),
            ]
            
            # Get answers for each question
            for question in all_questions:
                answer = response_obj.answer_set.filter(question=question).first()
                if answer:
                    # Format answer (parse JSON for multi-select/multi-text)
                    answer_text = answer.answer_text
                    if answer_text:
                        try:
                            parsed = json.loads(answer_text)
                            if isinstance(parsed, list):
                                answer_text = ', '.join(str(item) for item in parsed)
                        except (json.JSONDecodeError, ValueError):
                            pass
                    row.append(answer_text)
                else:
                    row.append('')
            
            writer.writerow(row)
        
        return response
    
    export_as_csv.short_description = 'Export selected responses to CSV'


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1
    fields = ('text', 'question_type', 'required', 'is_common')
    readonly_fields = ('is_common',)


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at', 'results_link')
    inlines = [QuestionInline]
    
    def results_link(self, obj):
        """Link to view survey results."""
        return format_html(
            '<a href="{}" class="button" style="background-color: #417690;">{}</a>',
            f'/surveys/{obj.id}/results/',
            _('View Results')
        )
    results_link.short_description = _('Results')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    # Show Survey first in the changelist and in the form
    list_display = ('survey', 'text', 'question_type', 'required', 'is_common')
    fields = ('survey', 'text', 'question_type', 'choices', 'max_selections', 'multi_text_count', 'required', 'groups')
    filter_horizontal = ('groups',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        # Provide clearer help text so admins understand selection semantics
        if db_field.name == 'groups':
            kwargs.setdefault('help_text', 'Select groups that SHOULD receive this question (leave empty = common to all)')
        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question', 'formatted_answer')

    def formatted_answer(self, obj):
        """Format answer_text: parse JSON for multi-select/multi-text, display as comma-separated list."""
        answer_text = obj.answer_text
        if not answer_text:
            return '-'
        
        # Try to parse as JSON (for multi-select and multi-text)
        try:
            parsed = json.loads(answer_text)
            if isinstance(parsed, list):
                return ', '.join(str(item) for item in parsed)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # Not JSON, return as-is (text or choice)
        return answer_text
    
    formatted_answer.short_description = 'Answer'


# Integrate Group assignment into the Django User admin so that when creating
# a user an admin can select which single Group they belong to.
User = get_user_model()
try:
    admin.site.unregister(User)
except Exception:
    pass


# Provide a ModelForm that includes a single group field so the
# admin can render it even though it's not a direct User model field.
from django import forms as _forms
UserModel = get_user_model()

class AdminUserForm(_forms.ModelForm):
    # single group selection using radio buttons (one user = one group)
    group = _forms.ModelChoiceField(
        queryset=Group.objects.all(), required=False,
        widget=_forms.RadioSelect(), label='Group'
    )

    class Meta:
        model = UserModel
        fields = ('username',)  # email intentionally omitted per request


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    # Remove the UserTypeAssignment inline from the admin UI
    inlines = ()

    # Use our custom forms for add/change so we can include the single group field
    form = AdminUserForm
    add_form = AdminUserForm

    # Show username, group, admin status, and active status in the changelist
    list_display = ('username', 'group_name', 'admin_status', 'active_status')

    # Hide the default admin list filters on the User changelist (no sidebar filters)
    list_filter = ()

    def group_name(self, obj):
        """Return the first assigned group name or '-' if none."""
        g = obj.groups.first()
        return g.name if g else '-'
    group_name.short_description = 'Group'

    def admin_status(self, obj):
        """Display if user is admin (superuser) with colored mark."""
        html = '<span style="color: {}; font-weight: bold;">{}</span>'
        if obj.is_superuser:
            return format_html(html, 'green', '✓')
        return format_html(html, 'red', '✗')
    admin_status.short_description = _('סטטוס משתמש על')
    
    def active_status(self, obj):
        """Display active status with colored mark."""
        html = '<span style="color: {}; font-weight: bold;">{}</span>'
        if obj.is_active:
            return format_html(html, 'green', '✓')
        return format_html(html, 'red', '✗')
    active_status.short_description = _('פעיל')

    # Simplify add form to only request username/email (no password field shown)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username',),
        }),
    )

    # Simplify change form fieldsets (omit password / auth-related widgets)
    fieldsets = (
        (None, {'fields': ('username',)}),
        ('Group', {'fields': ('group',)}),
        ('Status', {'fields': ('is_active', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def add_view(self, request, form_url='', extra_context=None):
        """Handle admin add-user POST in the same way as the public /users/ UI.

        - Validates username is present
        - Sets default password for new users
        - Assigns Group from the submitted group field
        - Redirects based on button pressed: Save and add another -> stay on add; Save and exit -> go to index
        """
        from django.contrib import messages
        from django.urls import reverse

        Form = self.get_form(request)
        extra_context = extra_context or {}
        # always provide groups for template rendering
        extra_context['groups'] = Group.objects.all()
        from django.urls import reverse
        if request.method == 'POST':
            form = Form(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                # default password for new users
                if not obj.pk:
                    # set default password from settings for newly created users
                    obj.set_password(getattr(settings, 'DEFAULT_USER_PASSWORD', 'password'))
                obj.save()
                # assignment: single group
                selected = form.cleaned_data.get('group')
                try:
                    if selected:
                        obj.groups.set([selected])
                    else:
                        obj.groups.clear()
                except Exception:
                    pass
                messages.success(request, f'User "{obj.username}" created.')
                if '_addanother' in request.POST:
                    return HttpResponseRedirect(reverse('admin:auth_user_add'))
                # After saving in admin, go back to the users changelist in admin
                return HttpResponseRedirect(reverse('admin:auth_user_changelist'))
            else:
                # Let the admin render the form with errors (our templates show errors)
                sel = request.POST.get('group')
                extra_context['presel'] = int(sel) if sel and sel.isdigit() else None
                return super().add_view(request, form_url, extra_context=extra_context)
        # For GET render a simplified admin add page that includes the group selector
        return render(request, 'surveys/admin_custom_add_user.html', extra_context)

    def save_model(self, request, obj, form, change):
        # For change view -- ensure single group assignment saved
        obj.save()
        try:
            selected = form.cleaned_data.get('group')
        except Exception:
            selected = None
        try:
            if selected:
                obj.groups.set([selected])
            else:
                obj.groups.clear()
        except Exception:
            pass

    def change_view(self, request, object_id, form_url='', extra_context=None):
        # Provide groups and current selection to the change template
        extra_context = extra_context or {}
        extra_context['groups'] = Group.objects.all()
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            obj = User.objects.get(pk=object_id)
            g = obj.groups.first()
            extra_context['presel'] = g.id if g else None
        except Exception:
            extra_context['presel'] = None
        # Use the default Django admin template for change view
        extra_context['change_form_template'] = 'admin/change_form.html'
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


# Customize the built-in auth Group admin to hide permissions and adjust buttons
from django.contrib.auth.models import Group
from django.contrib.auth.admin import GroupAdmin as DjangoGroupAdmin

try:
    admin.site.unregister(Group)
except Exception:
    pass


@admin.register(Group)
class GroupAdmin(DjangoGroupAdmin):
    # Hide permissions field from the admin form
    exclude = ('permissions',)
