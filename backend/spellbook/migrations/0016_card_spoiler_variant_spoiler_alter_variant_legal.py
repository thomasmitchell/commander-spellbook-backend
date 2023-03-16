# Generated by Django 4.1.5 on 2023-03-15 20:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spellbook', '0014_delete_variants_squashed_0015_cardinvariant_templateinvariant_variant_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='card',
            name='spoiler',
            field=models.BooleanField(default=False, help_text='Is this card from an upcoming set?', verbose_name='is spoiler'),
        ),
        migrations.AddField(
            model_name='variant',
            name='spoiler',
            field=models.BooleanField(default=False, help_text='Is this variant a spoiler?', verbose_name='is spoiler'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='variant',
            name='legal',
            field=models.BooleanField(help_text='Is this variant legal in Commander?', verbose_name='is legal'),
        ),
    ]