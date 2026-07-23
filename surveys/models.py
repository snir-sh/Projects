from django.db import models


class UserType(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


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
    required = models.BooleanField(default=False)
    # If user_types is empty, treat the question as common to all users
    user_types = models.ManyToManyField(UserType, blank=True, related_name='questions')
    surveys = models.ManyToManyField(Survey, blank=True, related_name='questions')

    def is_common(self):
        return self.user_types.count() == 0

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
