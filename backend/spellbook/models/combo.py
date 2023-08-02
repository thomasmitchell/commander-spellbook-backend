from django.db import models
from .mixins import ScryfallLinkMixin
from .card import Card
from .feature import Feature
from .template import Template
from .ingredient import IngredientInCombination
from .validators import MANA_VALIDATOR, TEXT_VALIDATORS
from .utils import recipe


class Combo(models.Model, ScryfallLinkMixin):
    class Kind(models.TextChoices):
        GENERATOR = 'G'
        UTILITY = 'U'
        GENERATOR_WITH_MANY_CARDS = 'M'
        DRAFT = 'D'

    uses = models.ManyToManyField(
        to=Card,
        related_name='used_in_combos',
        help_text='Cards that this combo uses',
        blank=True,
        verbose_name='used cards',
        through='CardInCombo')
    needs = models.ManyToManyField(
        to=Feature,
        related_name='needed_by_combos',
        help_text='Features that this combo needs',
        blank=True,
        verbose_name='needed features')
    requires = models.ManyToManyField(
        to=Template,
        related_name='required_by_combos',
        help_text='Templates that this combo requires',
        blank=True,
        verbose_name='required templates',
        through='TemplateInCombo')
    produces = models.ManyToManyField(
        to=Feature,
        related_name='produced_by_combos',
        help_text='Features that this combo produces',
        verbose_name='produced features')
    removes = models.ManyToManyField(
        to=Feature,
        related_name='removed_by_combos',
        help_text='Features that this combo removes',
        blank=True,
        verbose_name='removed features')
    mana_needed = models.CharField(blank=True, max_length=200, default='', help_text='Mana needed for this combo. Use the {1}{W}{U}{B}{R}{G}{B/P}... format.', validators=[MANA_VALIDATOR])
    other_prerequisites = models.TextField(blank=True, default='', help_text='Other prerequisites for this combo.', validators=TEXT_VALIDATORS)
    description = models.TextField(blank=True, help_text='Long description of the combo, in steps', validators=TEXT_VALIDATORS)
    kind = models.CharField(choices=Kind.choices, default=Kind.GENERATOR, help_text='Is this combo a generator for variants?', verbose_name='kind', max_length=2)
    created = models.DateTimeField(auto_now_add=True, editable=False)
    updated = models.DateTimeField(auto_now=True, editable=False)

    def cards(self):
        return self.uses.order_by('cardincombo')

    def templates(self):
        return self.requires.order_by('templateincombo')

    class Meta:
        ordering = ['created']
        verbose_name = 'combo'
        verbose_name_plural = 'combos'

    def __str__(self):
        if self.pk is None:
            return 'New, unsaved combo'
        return recipe([str(card) for card in self.cards()] + [str(feature) for feature in self.needs.all()] + [str(template) for template in self.templates()],
            [str(feature) for feature in self.produces.all()],
            [str(feature) for feature in self.removes.all()])


class CardInCombo(IngredientInCombination):
    card = models.ForeignKey(to=Card, on_delete=models.CASCADE)
    combo = models.ForeignKey(to=Combo, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.card} in combo {self.combo.pk}'

    class Meta(IngredientInCombination.Meta):
        unique_together = [('card', 'combo')]


class TemplateInCombo(IngredientInCombination):
    template = models.ForeignKey(to=Template, on_delete=models.CASCADE)
    combo = models.ForeignKey(to=Combo, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.template} in combo {self.combo.pk}'

    class Meta(IngredientInCombination.Meta):
        unique_together = [('template', 'combo')]
