# Generated by Django 5.0.1 on 2024-01-14 16:35

import django.db.models.manager
from django.db import migrations, models
from spellbook.models.ingredient import Recipe


def populate_name_field(apps, schema_editor):
    Variant = apps.get_model('spellbook', 'Variant')
    Combo = apps.get_model('spellbook', 'Combo')
    VariantSuggestion = apps.get_model('spellbook', 'VariantSuggestion')
    objs = list(Variant.objects.all().prefetch_related('uses', 'requires', 'produces'))
    for obj in objs:
        obj.name = Recipe.compute_name(
            cards=[c.name for c in obj.uses.order_by('cardinvariant')],
            templates=[t.name for t in obj.requires.order_by('templateinvariant')],
            features_needed=[],
            features_produced=[f.name for f in obj.produces.all()],
        )
    Variant.objects.bulk_update(objs, ['name'])
    objs = list(Combo.objects.all().prefetch_related('uses', 'requires', 'needs', 'removes', 'produces'))
    for obj in objs:
        obj.name = Recipe.compute_name(
            cards=[c.name for c in obj.uses.order_by('cardincombo')],
            templates=[t.name for t in obj.requires.order_by('templateincombo')],
            features_needed=[f.name for f in obj.needs.all()],
            features_produced=[f.name for f in obj.produces.all()],
        )
    Combo.objects.bulk_update(objs, ['name'])
    objs = list(VariantSuggestion.objects.all().prefetch_related('uses', 'requires', 'produces'))
    for obj in objs:
        obj.name = Recipe.compute_name(
            cards=[c.card for c in obj.uses.all()],
            templates=[t.template for t in obj.requires.all()],
            features_needed=[],
            features_produced=[f.feature for f in obj.produces.all()],
        )
    VariantSuggestion.objects.bulk_update(objs, ['name'])


class Migration(migrations.Migration):

    dependencies = [
        ('spellbook', '0009_preserialized_variants_and_gin_indexes'),
    ]

    operations = [
        migrations.AddField(
            model_name='combo',
            name='name',
            field=models.CharField(default='N/A', editable=False, max_length=3835),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variant',
            name='name',
            field=models.CharField(default='N/A', editable=False, max_length=3835),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='variantsuggestion',
            name='name',
            field=models.CharField(default='N/A', editable=False, max_length=3835),
            preserve_default=False,
        ),
        migrations.RunPython(
            populate_name_field,
            reverse_code=migrations.RunPython.noop,
        ),
        migrations.AlterModelManagers(
            name='variant',
            managers=[
                ('recipes_prefetched', django.db.models.manager.Manager()),
            ],
        ),
    ]
