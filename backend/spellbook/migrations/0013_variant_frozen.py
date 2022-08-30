# Generated by Django 4.0.6 on 2022-08-25 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spellbook', '0012_jobs_started_by_alter_jobs_expected_termination_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='variant',
            name='frozen',
            field=models.BooleanField(default=False, editable=False, help_text='Is this variant undeletable?', verbose_name='is frozen'),
        ),
    ]