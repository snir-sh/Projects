from django.db import models
from django.conf import settings
from django.contrib.auth.models import Group


class Survey(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Question(models.Model):
    TEXT = 'text'
    CHOICE = 'choice'
    QUESTION_TYPES = [(TEXT, 'Text'), (CHOICE, 'Choice')]

    text = models.TextField()
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPES, default=TEXT)
    # For choice questions, newline-separated options stored here (one per line)
    choices = models.TextField(blank=True, help_text='One option per line. Used when question_type is "Choice"')
    required = models.BooleanField(default=False)
    # Associate questions with Django auth Groups. If groups is empty, question is common to all users.
    groups = models.ManyToManyField(Group, blank=True, related_name='questions')
    # Each question belongs to a single Survey — create the Survey before adding Questions
    # Make nullable for now so migrations can be applied; later this can be made required
    survey = models.ForeignKey('Survey', on_delete=models.CASCADE, related_name='questions', null=True, blank=True)

    def is_common(self):
        return self.groups.count() == 0

    def __str__(self):
        return (self.text[:75] + '...') if len(self.text) > 75 else self.text


class Response(models.Model):
    survey = models.ForeignKey(Survey, on_delete=models.CASCADE, related_name='responses')
    user_identifier = models.CharField(max_length=200, help_text='Identifier for the respondent (user id, email, or anon token)')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Response {self.id} to {self.survey} by {self.user_identifier}"


class Answer(models.Model):
    response = models.ForeignKey(Response, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    answer_text = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Answer to {self.question}"
