# Generated migration for Response status and updated_at fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0003_question_max_selections_question_multi_text_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='response',
            name='status',
            field=models.CharField(
                choices=[('draft', 'Draft'), ('completed', 'Completed')],
                default='draft',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='response',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
