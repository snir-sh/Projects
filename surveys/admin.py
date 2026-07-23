from django.contrib import admin
from .models import UserType, Survey, Question, Response, Answer


@admin.register(UserType)
class UserTypeAdmin(admin.ModelAdmin):
    list_display = ('name',)


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
