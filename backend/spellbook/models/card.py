from urllib.parse import urlencode
from django.core.exceptions import ValidationError
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.db.models.fields.generated import GeneratedField
from .playable import Playable
from .utils import strip_accents, simplify_card_name_on_database, simplify_card_name_with_spaces_on_database
from .mixins import ScryfallLinkMixin, PreSaveModelMixin
from .feature import Feature


def validate_keyword_json(value):
    if not isinstance(value, list):
        raise ValidationError(f'Keywords must be a list of strings, got {type(value).__name__}')
    for i, keyword in enumerate(value):
        if not isinstance(keyword, str):
            raise ValidationError(f'Keyword at position {i + 1} must be a string, got {type(keyword).__name__}')


class Card(Playable, PreSaveModelMixin, ScryfallLinkMixin):
    MAX_CARD_NAME_LENGTH = 255
    oracle_id = models.UUIDField(unique=True, blank=True, null=True, help_text='Scryfall Oracle ID', verbose_name='Scryfall Oracle ID of card')
    name = models.CharField(max_length=MAX_CARD_NAME_LENGTH, unique=True, blank=False, help_text='Card name', verbose_name='name of card')
    name_unaccented = models.CharField(max_length=MAX_CARD_NAME_LENGTH, unique=True, blank=False, help_text='Card name without accents', verbose_name='name of card without accents', editable=False)
    name_unaccented_simplified = GeneratedField(
        db_persist=True,
        expression=simplify_card_name_on_database('name_unaccented'),
        output_field=models.CharField(max_length=MAX_CARD_NAME_LENGTH, unique=True, blank=False, help_text='Card name without accents or hyphens', verbose_name='name of card without accents or hyphens', editable=False))
    name_unaccented_simplified_with_spaces = GeneratedField(
        db_persist=True,
        expression=simplify_card_name_with_spaces_on_database('name_unaccented'),
        output_field=models.CharField(max_length=MAX_CARD_NAME_LENGTH, unique=True, blank=False, help_text='Card name without accents or hyphens, with spaces', verbose_name='name of card without accents or hyphens, with spaces', editable=False))

    @classmethod
    def scryfall_fields(cls):
        return [
            'type_line',
            'oracle_text',
            'keywords',
            'mana_value',
            'reserved',
            'latest_printing_set',
            'reprinted',
        ]
    type_line = models.CharField(max_length=MAX_CARD_NAME_LENGTH, blank=True, help_text='Card type line', verbose_name='type line of card')
    oracle_text = models.TextField(blank=True, help_text='Card oracle text', verbose_name='oracle text of card')
    keywords = models.JSONField(default=list, help_text='Oracle card keywords', verbose_name='oracle keywords of card', validators=[validate_keyword_json])
    mana_value = models.PositiveSmallIntegerField(default=0, help_text='Mana value of card', verbose_name='mana value of card')
    reserved = models.BooleanField(default=False, help_text='Whether this card is part of the Reserved List', verbose_name='reserved list card')
    latest_printing_set = models.CharField(max_length=10, blank=True, help_text='Set code of latest printing of card', verbose_name='latest printing set of card')
    reprinted = models.BooleanField(default=False, help_text='Whether this card has been reprinted', verbose_name='reprinted card')

    features = models.ManyToManyField(
        to=Feature,
        related_name='cards',
        help_text='Features provided by this single card effects or characteristics',
        blank=True)
    added = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    class Meta:
        ordering = ['name']
        verbose_name = 'card'
        verbose_name_plural = 'cards'

    def __str__(self):
        return self.name

    def query_string(self):
        return urlencode({'q': f'!"{self.name}"'})

    def pre_save(self):
        self.name_unaccented = strip_accents(self.name)


@receiver(post_save, sender=Card, dispatch_uid='update_variant_fields')
def update_variant_fields(sender, instance, created, raw, **kwargs):
    from .variant import Variant
    if raw:
        return
    if created:
        return
    variants = Variant.objects.prefetch_related('uses', 'cardinvariant_set', 'templateinvariant_set').filter(uses=instance)
    variants_to_save = []
    for variant in variants:
        requires_commander = any(civ.must_be_commander for civ in variant.cardinvariant_set.all()) \
            or any(tiv.must_be_commander for tiv in variant.templateinvariant_set.all())
        if variant.update(variant.uses.all(), requires_commander):
            variants_to_save.append(variant)
    Variant.objects.bulk_update(variants_to_save, fields=Variant.playable_fields())
