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
    inlines = (UserTypeAssignmentInline,)
