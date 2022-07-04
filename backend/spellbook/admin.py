from django.contrib import admin
from django.urls import path, reverse
from django.http import HttpResponseRedirect

from .variants import generate_variants
from .models import Card, Feature, Combo, Variant

@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Scryfall', {'fields': ['oracle_id']}),
        ('Spellbook', {'fields': ['name', 'features']})
    ]
    # inlines = [FeatureInline]
    search_fields = ['name', 'features__name']
    autocomplete_fields = ['features']
    list_filter = ['features__name']
    list_display = ['name', 'id']

class CardInline(admin.StackedInline):
    model = Feature.cards.through
    extra = 1
    autocomplete_fields = ['card']

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'description']}),
    ]
    inlines = [CardInline]
    search_fields = ['name', 'cards__name']
    list_display = ['name', 'id']


@admin.register(Variant)
class VariantAdmin(admin.ModelAdmin):
    readonly_fields = ['includes', 'produces', 'of', 'unique_id']
    fieldsets = [
        ('Generated', {'fields': ['unique_id', 'includes', 'produces', 'of']}),
        ('Editable', {'fields': ['status', 'prerequisites', 'description']})
    ]
    list_filter = ['status']
    list_display = ['__str__', 'status']

    def generate(self, request):
        generate_variants()
        return HttpResponseRedirect(reverse('admin:spellbook_variant_changelist'))

    def get_urls(self):
        return [
            path('generate/', 
                self.admin_site.admin_view(view=self.generate, cacheable=False),
                name='spellbook_variant_generate')
            ] + super().get_urls()

    def has_add_permission(self, request):
        return False
    def has_change_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Combo)
class ComboAdmin(admin.ModelAdmin):
    fieldsets = [
        ('Requirements', {'fields': ['includes', 'needs', 'prerequisites']}),
        ('Features', {'fields': ['produces']}),
        ('Description', {'fields': ['description']})
    ]
    filter_horizontal = ['includes', 'produces', 'needs']
    list_filter = ['produces', 'needs']
    search_fields = ['includes__name', 'produces__name', 'needs__name']
    list_display = ['__str__', 'id']


# Admin configuration
admin.site.site_header = 'Spellbook Admin Panel'
admin.site.site_title = 'Spellbook Admin'
admin.site.index_title = 'Spellbook Admin Index'