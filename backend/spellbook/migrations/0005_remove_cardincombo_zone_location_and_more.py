# Generated by Django 4.1.5 on 2023-04-03 19:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('spellbook', '0004_alter_combo_mana_needed_alter_variant_mana_needed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cardincombo',
            name='zone_location',
        ),
        migrations.RemoveField(
            model_name='cardinvariant',
            name='zone_location',
        ),
        migrations.RemoveField(
            model_name='templateincombo',
            name='zone_location',
        ),
        migrations.RemoveField(
            model_name='templateinvariant',
            name='zone_location',
        ),
        migrations.AddField(
            model_name='cardincombo',
            name='zone_locations',
            field=models.CharField(default='H', help_text='Starting location(s) for the card.', max_length=6, verbose_name='starting location'),
        ),
        migrations.AddField(
            model_name='cardinvariant',
            name='zone_locations',
            field=models.CharField(default='H', help_text='Starting location(s) for the card.', max_length=6, verbose_name='starting location'),
        ),
        migrations.AddField(
            model_name='templateincombo',
            name='zone_locations',
            field=models.CharField(default='H', help_text='Starting location(s) for the card.', max_length=6, verbose_name='starting location'),
        ),
        migrations.AddField(
            model_name='templateinvariant',
            name='zone_locations',
            field=models.CharField(default='H', help_text='Starting location(s) for the card.', max_length=6, verbose_name='starting location'),
        ),
    ]
