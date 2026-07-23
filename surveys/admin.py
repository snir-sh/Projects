from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
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


@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):
    # Remove the UserTypeAssignment inline from the admin UI
    inlines = ()

    # Simplify add form to only request username/email (no password field shown)
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email'),
        }),
    )

    # Simplify change form fieldsets (omit password / auth-related widgets)
    fieldsets = (
        (None, {'fields': ('username', 'email')}),
        ('Status', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    def save_model(self, request, obj, form, change):
        # For newly created users (via admin), set a default password and save
        if not obj.pk:
            obj.set_password('password')
        obj.save()


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
