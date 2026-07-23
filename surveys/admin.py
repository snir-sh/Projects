from django import forms
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.forms.widgets import CheckboxSelectMultiple
from django.http import HttpResponseRedirect
from .models import UserType, Survey, Question, Response, Answer, UserTypeAssignment


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


class UserTypeAssignmentInline(admin.TabularInline):
    model = UserTypeAssignment
    extra = 0


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Response)
class ResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'survey', 'user_identifier', 'submitted_at')
    inlines = [AnswerInline]


@admin.register(Survey)
class SurveyAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_at')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'question_type', 'required', 'is_common')
    filter_horizontal = ('user_types', 'surveys')


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('response', 'question')


# Integrate UserType assignment into the Django User admin so that when creating
# a user an admin can select which UserType/group(s) they belong to.
User = get_user_model()
try:
    admin.site.unregister(User)
except Exception:
    pass


# Provide a ModelForm that includes a user_types field (checkboxes) so the
# admin can render it even though it's not a direct User model field.
from django import forms as _forms
UserModel = get_user_model()

class AdminUserForm(_forms.ModelForm):
    user_types = _forms.ModelMultipleChoiceField(
        queryset=UserType.objects.all(), required=False, widget=CheckboxSelectMultiple, label='Groups'
    )

    class Meta:
        model = UserModel
        fields = ('username',)  # email intentionally omitted per request


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    # Remove the UserTypeAssignment inline from the admin UI
    inlines = ()

    # Use our custom forms for add/change so we can include user_types
    form = AdminUserForm
    add_form = AdminUserForm

    # Hide the default admin list filters on the User changelist (no sidebar filters)
    list_filter = ()

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
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    change_form_template = 'admin/auth/user/change_form.html'
    add_form_template = 'admin/auth/user/add_form.html'

    def add_view(self, request, form_url='', extra_context=None):
        """Handle admin add-user POST in the same way as the public /users/ UI.

        - Validates username is present
        - Sets default password for new users
        - Assigns UserType groups from the submitted user_types field
        - Redirects based on button pressed: Save and add another -> stay on add; Save and exit -> go to index
        """
        from django.contrib import messages
        from django.urls import reverse

        Form = self.get_form(request)
        if request.method == 'POST':
            form = Form(request.POST)
            if form.is_valid():
                obj = form.save(commit=False)
                # default password for new users
                if not obj.pk:
                    obj.set_password('password')
                obj.save()
                # assignments
                selected = form.cleaned_data.get('user_types', []) or []
                UserTypeAssignment.objects.filter(user=obj).delete()
                for ut in selected:
                    UserTypeAssignment.objects.get_or_create(user=obj, user_type=ut)
                messages.success(request, f'User "{obj.username}" created.')
                if '_addanother' in request.POST:
                    return HttpResponseRedirect(reverse('admin:auth_user_add'))
                return HttpResponseRedirect(reverse('index'))
            else:
                # Let the admin render the form with errors (our templates show errors)
                extra_context = extra_context or {}
                extra_context['presel'] = [int(x) for x in request.POST.getlist('user_types') if x.isdigit()]
                return super().add_view(request, form_url, extra_context=extra_context)
        return super().add_view(request, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        # For change view -- ensure assignments saved
        obj.save()
        try:
            selected = form.cleaned_data.get('user_types', [])
        except Exception:
            selected = []
        UserTypeAssignment.objects.filter(user=obj).delete()
        for ut in selected:
            UserTypeAssignment.objects.get_or_create(user=obj, user_type=ut)


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
    # Use a custom template for the change form so button labels can be adjusted
    change_form_template = 'admin/auth/group/change_form.html'
