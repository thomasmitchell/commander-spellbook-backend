from django.contrib import admin, messages
from django.forms import ModelForm
from ..models import Combo, CardInCombo, TemplateInCombo, Variant, CardInVariant, TemplateInVariant
from ..variants.combo_graph import MAX_CARDS_IN_COMBO
from ..variants.variant_data import RestoreData
from ..variants.variants_generator import restore_variant
from .mixins import SearchMultipleRelatedMixin


class ComboForm(ModelForm):
    def clean_mana_needed(self):
        return self.cleaned_data['mana_needed'].upper() if self.cleaned_data['mana_needed'] else self.cleaned_data['mana_needed']


class IngredientInComboForm(ModelForm):
    def clean(self):
        if hasattr(self.cleaned_data['combo'], 'ingredient_count'):
            self.cleaned_data['combo'].ingredient_count += 1
        else:
            self.cleaned_data['combo'].ingredient_count = 1
        self.instance.order = self.cleaned_data['combo'].ingredient_count
        return super().clean()


class CardInComboAdminInline(admin.TabularInline):
    fields = ['card', 'zone_location', 'card_state']
    form = IngredientInComboForm
    model = CardInCombo
    extra = 0
    verbose_name = 'Card'
    verbose_name_plural = 'Required Cards'
    autocomplete_fields = ['card']
    max_num = MAX_CARDS_IN_COMBO


class TemplateInComboAdminInline(admin.TabularInline):
    fields = ['template', 'zone_location', 'card_state']
    form = IngredientInComboForm
    model = TemplateInCombo
    extra = 0
    verbose_name = 'Template'
    verbose_name_plural = 'Required Templates'
    autocomplete_fields = ['template']
    max_num = MAX_CARDS_IN_COMBO


class FeatureInComboAdminInline(admin.TabularInline):
    model = Combo.needs.through
    extra = 0
    verbose_name = 'Feature'
    verbose_name_plural = 'Required Features'
    autocomplete_fields = ['feature']
    max_num = MAX_CARDS_IN_COMBO


@admin.register(Combo)
class ComboAdmin(SearchMultipleRelatedMixin, admin.ModelAdmin):
    form = ComboForm
    save_as = True
    readonly_fields = ['scryfall_link']
    fieldsets = [
        ('Generated', {'fields': ['scryfall_link']}),
        ('More Requirements', {'fields': [
            'mana_needed',
            'other_prerequisites']}),
        ('Features', {'fields': ['produces', 'removes']}),
        ('Description', {'fields': ['generator', 'description']}),
    ]
    inlines = [CardInComboAdminInline, TemplateInComboAdminInline, FeatureInComboAdminInline]
    filter_horizontal = ['uses', 'produces', 'needs', 'removes']
    list_filter = ['generator']
    search_fields = ['uses__name', 'requires__name', 'produces__name', 'needs__name']
    list_display = ['__str__', 'generator', 'id']

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('uses', 'requires', 'produces', 'needs', 'removes')

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        if change:
            query = form.instance.variants.filter(status__in=[Variant.Status.NEW, Variant.Status.RESTORE])
            count = query.count()
            if count <= 0:
                return
            if count >= 1000:
                messages.warning(request, f'{count} "New" or "Restore" variants are too many to update for this combo: no automatic update was done.')
                return
            variants_to_update = list[Variant]()
            card_in_variants_to_update = list[CardInVariant]()
            template_in_variants_to_update = list[TemplateInVariant]()
            data = RestoreData()
            for variant in list[Variant](query):
                uses_set, requires_set = restore_variant(
                    variant,
                    list(variant.includes.all()),
                    list(variant.of.all()),
                    list(variant.cardinvariant_set.all()),
                    list(variant.templateinvariant_set.all()),
                    data=data)
                card_in_variants_to_update.extend(uses_set)
                template_in_variants_to_update.extend(requires_set)
            update_fields = ['status', 'mana_needed', 'other_prerequisites', 'description', 'legal', 'identity']
            Variant.objects.bulk_update(variants_to_update, update_fields)
            update_fields = ['zone_location', 'card_state', 'order']
            CardInVariant.objects.bulk_update(card_in_variants_to_update, update_fields)
            TemplateInVariant.objects.bulk_update(template_in_variants_to_update, update_fields)
            messages.info(request, f'{count} "New" or "Restore" variants were updated for this combo.')
