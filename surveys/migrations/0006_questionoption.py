from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0005_alter_answer_options_alter_question_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionOption',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=255)),
                ('image', models.FileField(blank=True, upload_to='question_option_images/')),
                ('order', models.PositiveIntegerField(default=0)),
                ('question', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='option_items', to='surveys.question')),
            ],
            options={
                'verbose_name': 'Question option',
                'verbose_name_plural': 'Question options',
                'ordering': ['order', 'id'],
            },
        ),
    ]
