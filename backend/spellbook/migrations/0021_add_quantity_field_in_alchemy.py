# Generated by Django 5.0.4 on 2024-05-03 13:26

import django.db.models.deletion
import django.core.validators
from django.db import migrations, models
from spellbook.serializers import VariantSerializer


def migrate_variant_produces_through(apps, schema_editor):
    FeatureProducedByVariant = apps.get_model('spellbook', 'FeatureProducedByVariant')
    Variant = apps.get_model('spellbook', 'Variant')
    to_create = []
    for variant in Variant.objects.prefetch_related('produces'):
        for feature in variant.produces.all():
            to_create.append(
                FeatureProducedByVariant(
                    variant=variant,
                    feature=feature,
                    quantity=1,
                )
            )
    FeatureProducedByVariant.objects.bulk_create(to_create)


def reverse_migrate_variant_produces_through(apps, schema_editor):
    FeatureProducedByVariant = apps.get_model('spellbook', 'FeatureProducedByVariant')
    FeatureProducedByVariantOld = apps.get_model('spellbook', 'Variant').produces.through
    to_create = []
    for feature_produced_by_variant in FeatureProducedByVariant.objects.all():
        to_create.append(FeatureProducedByVariantOld(
            variant_id=feature_produced_by_variant.variant_id,
            feature_id=feature_produced_by_variant.feature_id,
        ))
    for i, obj in enumerate(to_create):
        obj.id = i + 1
        obj.save(force_insert=True)


def migrate_combo_produces_through(apps, schema_editor):
    FeatureProducedInCombo = apps.get_model('spellbook', 'FeatureProducedInCombo')
    Combo = apps.get_model('spellbook', 'Combo')
    to_create = []
    for combo in Combo.objects.prefetch_related('produces'):
        for feature in combo.produces.all():
            to_create.append(
                FeatureProducedInCombo(
                    combo=combo,
                    feature=feature,
                )
            )
    FeatureProducedInCombo.objects.bulk_create(to_create)


def reverse_migrate_combo_produces_through(apps, schema_editor):
    FeatureProducedInCombo = apps.get_model('spellbook', 'FeatureProducedInCombo')
    FeatureProducedInComboOld = apps.get_model('spellbook', 'Combo').produces.through
    to_create = []
    for feature_produced_in_combo in FeatureProducedInCombo.objects.all():
        to_create.append(FeatureProducedInComboOld(
            combo_id=feature_produced_in_combo.combo_id,
            feature_id=feature_produced_in_combo.feature_id,
        ))
    for i, obj in enumerate(to_create):
        obj.id = i + 1
        obj.save(force_insert=True)


def migrate_feature_removed_in_combo_through(apps, schema_editor):
    FeatureRemovedInCombo = apps.get_model('spellbook', 'FeatureRemovedInCombo')
    Combo = apps.get_model('spellbook', 'Combo')
    to_create = []
    for combo in Combo.objects.prefetch_related('removes'):
        for feature in combo.removes.all():
            to_create.append(
                FeatureRemovedInCombo(
                    combo=combo,
                    feature=feature,
                )
            )
    FeatureRemovedInCombo.objects.bulk_create(to_create)


def reverse_migrate_feature_removed_in_combo_through(apps, schema_editor):
    FeatureRemovedInCombo = apps.get_model('spellbook', 'FeatureRemovedInCombo')
    FeatureRemovedInComboOld = apps.get_model('spellbook', 'Combo').removes.through
    to_create = []
    for feature_removed_in_combo in FeatureRemovedInCombo.objects.all():
        to_create.append(FeatureRemovedInComboOld(
            combo_id=feature_removed_in_combo.combo_id,
            feature_id=feature_removed_in_combo.feature_id,
        ))
    for i, obj in enumerate(to_create):
        obj.id = i + 1
        obj.save(force_insert=True)


def migrate_variant_includes_through(apps, schema_editor):
    VariantIncludesCombo = apps.get_model('spellbook', 'VariantIncludesCombo')
    Variant = apps.get_model('spellbook', 'Variant')
    to_create = []
    for variant in Variant.objects.prefetch_related('includes'):
        for combo in variant.includes.all():
            to_create.append(
                VariantIncludesCombo(
                    variant=variant,
                    combo=combo,
                )
            )
    VariantIncludesCombo.objects.bulk_create(to_create)


def reverse_migrate_variant_includes_through(apps, schema_editor):
    VariantIncludesCombo = apps.get_model('spellbook', 'VariantIncludesCombo')
    VariantIncludesComboOld = apps.get_model('spellbook', 'Variant').includes.through
    to_create = []
    for variant_includes_combo in VariantIncludesCombo.objects.all():
        to_create.append(VariantIncludesComboOld(
            variant_id=variant_includes_combo.variant_id,
            combo_id=variant_includes_combo.combo_id,
        ))
    for i, obj in enumerate(to_create):
        obj.id = i + 1
        obj.save(force_insert=True)


def migrate_variant_of_combo_through(apps, schema_editor):
    VariantOfCombo = apps.get_model('spellbook', 'VariantOfCombo')
    Combo = apps.get_model('spellbook', 'Combo')
    Variant = apps.get_model('spellbook', 'Variant')
    to_create = []
    for variant in Variant.objects.prefetch_related('of'):
        for combo in variant.of.all():
            to_create.append(
                VariantOfCombo(
                    variant=variant,
                    combo=combo,
                )
            )
    VariantOfCombo.objects.bulk_create(to_create)


def reverse_migrate_variant_of_combo_through(apps, schema_editor):
    VariantOfCombo = apps.get_model('spellbook', 'VariantOfCombo')
    VariantOfComboOld = apps.get_model('spellbook', 'Variant').of.through
    to_create = []
    for variant_of_combo in VariantOfCombo.objects.all():
        to_create.append(VariantOfComboOld(
            variant_id=variant_of_combo.variant_id,
            combo_id=variant_of_combo.combo_id,
        ))
    for i, obj in enumerate(to_create):
        obj.id = i + 1
        obj.save(force_insert=True)


def update_serialized_representation(apps, schema_editor):
    Variant = apps.get_model('spellbook', 'Variant')
    FeatureProducedByVariant = apps.get_model('spellbook', 'FeatureProducedByVariant')
    variants_source = list(Variant.objects
        .prefetch_related(
            'cardinvariant_set',
            'templateinvariant_set',
            models.Prefetch(
                'featureproducedbyvariant_set',
                queryset=FeatureProducedByVariant.objects
                .select_related('feature')
                .filter(feature__utility=False),
            ),
            'cardinvariant_set__card',
            'templateinvariant_set__template',
            'of',
            'includes',
        )
    )
    for variant in variants_source:
        variant.pre_save = lambda: None
        variant.serialized = VariantSerializer(variant).data  # type: ignore
    Variant.objects.bulk_update(objs=variants_source, fields=['serialized'], batch_size=5000)  # type: ignore


class Migration(migrations.Migration):

    dependencies = [
        ('spellbook', '0020_cardusedinvariantsuggestion_card_unaccented_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='cardincombo',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='cardinvariant',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='cardusedinvariantsuggestion',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='featureneededincombo',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the feature needed in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='featureofcard',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='templateincombo',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='templateinvariant',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.AddField(
            model_name='templaterequiredinvariantsuggestion',
            name='quantity',
            field=models.PositiveSmallIntegerField(default=1, help_text='Quantity of the card in the combo.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity'),
        ),
        migrations.CreateModel(
            name='FeatureProducedByVariant',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('quantity', models.PositiveSmallIntegerField(default=1, help_text='Quantity of the feature produced by the variant.', validators=[django.core.validators.MinValueValidator(1)], verbose_name='quantity')),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.feature')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.variant')),
            ],
            options={
                'unique_together': {('feature', 'variant')},
            },
        ),
        migrations.RunPython(
            code=migrate_variant_produces_through,
            reverse_code=reverse_migrate_variant_produces_through,
        ),
        migrations.RemoveField(
            model_name='variant',
            name='produces',
        ),
        migrations.AddField(
            model_name='variant',
            name='produces',
            field=models.ManyToManyField(editable=False, help_text='Features that this variant produces', related_name='produced_by_variants', through='spellbook.FeatureProducedByVariant', to='spellbook.feature'),
        ),
        migrations.CreateModel(
            name='FeatureProducedInCombo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.combo')),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.feature')),
            ],
            options={
                'unique_together': {('feature', 'combo')},
            },
        ),
        migrations.RunPython(
            code=migrate_combo_produces_through,
            reverse_code=reverse_migrate_combo_produces_through,
        ),
        migrations.RemoveField(
            model_name='combo',
            name='produces',
        ),
        migrations.AddField(
            model_name='combo',
            name='produces',
            field=models.ManyToManyField(help_text='Features that this combo produces', related_name='produced_by_combos', through='spellbook.FeatureProducedInCombo', to='spellbook.feature', verbose_name='produced features'),
        ),
        migrations.CreateModel(
            name='FeatureRemovedInCombo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.combo')),
                ('feature', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.feature')),
            ],
            options={
                'unique_together': {('feature', 'combo')},
            },
        ),
        migrations.RunPython(
            code=migrate_feature_removed_in_combo_through,
            reverse_code=reverse_migrate_feature_removed_in_combo_through,
        ),
        migrations.RemoveField(
            model_name='combo',
            name='removes',
        ),
        migrations.AddField(
            model_name='combo',
            name='removes',
            field=models.ManyToManyField(blank=True, help_text='Features that this combo removes', related_name='removed_by_combos', through='spellbook.FeatureRemovedInCombo', to='spellbook.feature', verbose_name='removed features'),
        ),
        migrations.CreateModel(
            name='VariantIncludesCombo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.combo')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.variant')),
            ],
            options={
                'unique_together': {('variant', 'combo')},
            },
        ),
        migrations.RunPython(
            code=migrate_variant_includes_through,
            reverse_code=reverse_migrate_variant_includes_through,
        ),
        migrations.RemoveField(
            model_name='variant',
            name='includes',
        ),
        migrations.AddField(
            model_name='variant',
            name='includes',
            field=models.ManyToManyField(editable=False, help_text='Combo that this variant includes', related_name='included_in_variants', through='spellbook.VariantIncludesCombo', to='spellbook.combo'),
        ),
        migrations.CreateModel(
            name='VariantOfCombo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('combo', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.combo')),
                ('variant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='spellbook.variant')),
            ],
            options={
                'unique_together': {('variant', 'combo')},
            },
        ),
        migrations.RunPython(
            code=migrate_variant_of_combo_through,
            reverse_code=reverse_migrate_variant_of_combo_through,
        ),
        migrations.RemoveField(
            model_name='variant',
            name='of',
        ),
        migrations.AddField(
            model_name='variant',
            name='of',
            field=models.ManyToManyField(editable=False, help_text='Combo that this variant is an instance of', related_name='variants', through='spellbook.VariantOfCombo', to='spellbook.combo'),
        ),
        migrations.RunPython(
            code=update_serialized_representation,
            reverse_code=migrations.RunPython.noop,
        ),
    ]
