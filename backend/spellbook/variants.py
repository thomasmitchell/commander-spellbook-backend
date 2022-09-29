import json
import hashlib
import logging
import pyomo.environ as pyo
from dataclasses import dataclass
from itertools import starmap
from django.db import transaction
from django.conf import settings
from .models import Card, Feature, Combo, Job, Variant
from pyomo.opt import TerminationCondition
from pyomo.opt.base.solvers import OptSolver


RECURSION_LIMIT = 20
# SOLVE_TIMEOUT = 5
MAX_CARDS_IN_COMBO = 10


@dataclass
class Data:
    def __init__(self):
        self.combos = Combo.objects.prefetch_related('uses', 'needs', 'removes')
        self.features = Feature.objects.prefetch_related('cards', 'produced_by_combos')
        self.cards = Card.objects.all()
        self.variants = Variant.objects.prefetch_related('uses')
        self.utility_features_ids = frozenset[int](Feature.objects.filter(utility=True).values_list('id', flat=True))


def unique_id_from_cards_ids(cards: list[int]) -> str:
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(json.dumps(sorted(cards)).encode('utf-8'))
    return hash_algorithm.hexdigest()


def priority_dict_for_combo(combo: Combo, recursion_counter=0) -> dict[int, int]:
    if recursion_counter > RECURSION_LIMIT:
        raise Exception('Recursion limit reached with combo {}'.format(combo.id))
    result = dict[int, int]()
    for card in combo.uses.all():
        result[card.id] = recursion_counter
    for feature in combo.needs.all():
        for card in feature.cards.all():
            result[card.id] = recursion_counter + 1
        for combo in feature.produced_by_combos.all():
            p1 = priority_dict_for_combo(combo, recursion_counter + 2)
            result = p1 | result
    return result


def check_combo_sanity(combo: Combo, recursion_counter: int = 0) -> bool:
    if recursion_counter > RECURSION_LIMIT:
        return False
    for feature in combo.needs.all():
        for combo in feature.produced_by_combos.all():
            if not check_combo_sanity(combo, recursion_counter + 1):
                return False
    return True


def removed_features(variant: Variant, features: set[int]) -> set[int]:
    return features - set(variant.includes.values_list('removes__id', flat=True))


def update_variant(
        data: Data,
        unique_id: str,
        combos_that_generated: set[int],
        combos_included: set[int],
        features: set[int],
        ok: bool,
        restore=False):
    variant = data.variants.get(unique_id=unique_id)
    variant.of.set(combos_that_generated)
    variant.includes.set(combos_included)
    variant.produces.set(removed_features(variant, features) - data.utility_features_ids)
    if restore:
        combos = data.combos.filter(id__in=combos_included)
        zone_locations = '\n'.join(c.zone_locations for c in combos if len(c.zone_locations) > 0)
        cards_state = '\n'.join(c.cards_state for c in combos if len(c.cards_state) > 0)
        other_prerequisites = '\n'.join(c.other_prerequisites for c in combos if len(c.other_prerequisites) > 0)
        mana_needed = ' '.join(c.mana_needed for c in combos if len(c.mana_needed) > 0)
        description = '\n'.join(c.description for c in combos if len(c.description) > 0)
        variant.zone_locations = zone_locations
        variant.cards_state = cards_state
        variant.other_prerequisites = other_prerequisites
        variant.mana_needed = mana_needed
        variant.description = description
        variant.status = Variant.Status.NEW if ok else Variant.Status.NOT_WORKING
    if not ok:
        variant.status = Variant.Status.NOT_WORKING
    if not ok or restore:
        variant.save()
    return variant.id


def create_variant(
        data: Data,
        unique_id: str,
        cards: list[int],
        combos_that_generated: set[int],
        combos_included: set[int],
        features: set[int],
        ok: bool):
    combos = data.combos.filter(id__in=combos_included)
    zone_locations = '\n'.join(c.zone_locations for c in combos if len(c.zone_locations) > 0)
    cards_state = '\n'.join(c.cards_state for c in combos if len(c.cards_state) > 0)
    other_prerequisites = '\n'.join(c.other_prerequisites for c in combos if len(c.other_prerequisites) > 0)
    mana_needed = ' '.join(c.mana_needed for c in combos if len(c.mana_needed) > 0)
    description = '\n'.join(c.description for c in combos if len(c.description) > 0)
    variant = Variant(
        unique_id=unique_id,
        zone_locations=zone_locations,
        cards_state=cards_state,
        other_prerequisites=other_prerequisites,
        mana_needed=mana_needed,
        description=description)
    if not ok:
        variant.status = Variant.Status.NOT_WORKING
    variant.save()
    variant.uses.set(cards)
    variant.of.set(combos_that_generated)
    variant.includes.set(combos_included)
    variant.produces.set(removed_features(variant, features) - data.utility_features_ids)
    return variant.id


def create_solver() -> OptSolver:
    return pyo.SolverFactory(settings.SOLVER_NAME)


def base_model(data: Data) -> pyo.ConcreteModel | None:
    model = pyo.ConcreteModel(name='Spellbook')
    model.B = pyo.Set(initialize=data.combos.values_list('id', flat=True))
    model.F = pyo.Set(initialize=data.features.values_list('id', flat=True))
    model.C = pyo.Set(initialize=data.cards.values_list('id', flat=True))
    if len(model.C) == 0:
        return None
    model.b = pyo.Var(model.B, domain=pyo.Boolean)
    model.f = pyo.Var(model.F, domain=pyo.Boolean)
    model.c = pyo.Var(model.C, domain=pyo.Boolean)
    # Variants constraints
    model.V = pyo.Constraint(expr=sum(model.c[i] for i in model.c) <= MAX_CARDS_IN_COMBO)
    # Combo constraints
    model.BC = pyo.ConstraintList()
    model.BF = pyo.ConstraintList()
    model.BCF = pyo.ConstraintList()
    for combo in data.combos:
        b = model.b[combo.id]
        used = combo.uses.all()
        card_vars = []
        for card in used:
            c = model.c[card.id]
            card_vars.append(c)
            model.BC.add(b <= c)
        needed = combo.needs.all()
        feature_vars = []
        for feature in needed:
            f = model.f[feature.id]
            feature_vars.append(f)
            model.BF.add(b <= f)
        model.BCF.add(b >= sum(card_vars + feature_vars) - len(card_vars) - len(feature_vars) + 1)
    # Feature constraints
    model.FC = pyo.ConstraintList()
    model.FB = pyo.ConstraintList()
    model.FCB = pyo.ConstraintList()
    for feature in data.features:
        f = model.f[feature.id]
        cards = feature.cards.all()
        card_vars = []
        for card in cards:
            c = model.c[card.id]
            card_vars.append(c)
            model.FC.add(f >= c)
        combo_vars = []
        for combo in feature.produced_by_combos.all():
            b = model.b[combo.id]
            combo_vars.append(b)
            model.FB.add(f >= b)
        model.FCB.add(f <= sum(card_vars + combo_vars))
    # Minimize cards, maximize features and combos
    feature_count = len(model.F)
    combo_count = len(model.B)
    model.MinMaxObj = pyo.Objective(
        expr=sum(
            model.b[i] for i in model.b) + sum(
            model.f[i] * (combo_count + 1) for i in model.f) - sum(
            model.c[i] * ((combo_count + 1) * (feature_count + 1)) for i in model.c),
        sense=pyo.maximize)
    model.MinMaxObj.deactivate()
    model.Variants = pyo.ConstraintList()
    return model


def combo_model(base_model: pyo.ConcreteModel, combo: Combo) -> pyo.ConcreteModel:
    model = base_model.clone()
    model.XB = pyo.Constraint(expr=model.b[combo.id] >= 1)
    return model


def exclude_variants_model(base_model: pyo.ConcreteModel, data: Data) -> pyo.ConcreteModel:
    model = base_model.clone()
    not_working_variants = data.variants.filter(status=Variant.Status.NOT_WORKING)
    for variant in not_working_variants:
        card_id_list = variant.uses.values_list('id', flat=True)
        model.Variants.add(sum(model.c[i] for i in card_id_list) <= len(card_id_list) - 1)
    model.obj = pyo.Objective(expr=sum(model.f[i] for i in model.f) + sum(model.b[i] for i in model.b), sense=pyo.maximize)
    return model


def is_variant_valid(model: pyo.ConcreteModel, card_ids: list[int]) -> bool:
    opt = create_solver()
    model.c.fix(False)
    for card_id in card_ids:
        model.c[card_id].fix(True)
    result = opt.solve(model, tee=False)
    answer = result.solver.termination_condition == TerminationCondition.optimal
    return answer


def solve_combo_model(model: pyo.ConcreteModel, opt: OptSolver) -> bool:
    model.MinMaxObj.activate()
    results = opt.solve(model, tee=False)
    model.MinMaxObj.deactivate()
    if results.solver.termination_condition == TerminationCondition.optimal:
        return True
    return False


@dataclass
class VariantDefinition:
    card_ids: list[int]
    of_ids: set[int]
    feature_ids: set[int]
    included_ids: set[int]


def get_variants_from_model(base_model: pyo.ConcreteModel, data: Data) -> dict[str, VariantDefinition]:
    def variants_from_combo(n: int, tot: int, base_model: pyo.ConcreteModel, combo: Combo) -> dict[str, VariantDefinition]:
        model = combo_model(base_model, combo)
        priorityc = priority_dict_for_combo(combo)
        result: dict[str, VariantDefinition] = {}
        opt = create_solver()
        while True:
            if solve_combo_model(model, opt):
                # Selecting only variables with a value of 1
                card_id_list = sorted([v for v in model.c if model.c[v].value == 1], key=lambda c: priorityc[c])
                feature_id_list = {v for v in model.f if model.f[v].value == 1}
                combo_id_list = {v for v in model.b if model.b[v].value == 1}
                unique_id = unique_id_from_cards_ids(card_id_list)
                result[unique_id] = VariantDefinition(card_ids=card_id_list, of_ids=frozenset({combo.id}), included_ids=combo_id_list, feature_ids=feature_id_list)
                # Eclude any solution containing the current variant of the combo, from now on
                model.Variants.add(sum(model.c[i] for i in card_id_list) <= len(card_id_list) - 1)
            else:
                break
        logging.info(f'Computed variants for combo {n}/{tot}')
        return result
    logging.info('Computing all possible variants')
    combos = data.combos.filter(generator=True)
    total = combos.count()
    results = list(starmap(variants_from_combo,
        ((i, total, base_model, c) for i, c in enumerate(combos, start=1))))
    logging.info('Merging results, discarding duplicates...')
    result = dict[str, VariantDefinition]()
    for r in results:
        for k, v in r.items():
            if k in result:
                v.of_ids |= result[k].of_ids
            result[k] = v
    logging.info('Done.')
    return result


def generate_variants(job: Job = None) -> tuple[int, int]:
    with transaction.atomic():
        logging.info('Fetching variants set to RESTORE...')
        to_restore = set(Variant.objects.filter(status=Variant.Status.RESTORE).values_list('unique_id', flat=True))
        logging.info('Fetching all variant unique ids...')
        data = Data()
        old_id_set = set(data.variants.values_list('unique_id', flat=True))
        logging.info('Computing combos MILP representation...')
        model = base_model(data)
        if model is not None:
            variant_check_model = exclude_variants_model(model, data)
            logging.info('Solving MILP for each combo...')
            variants = get_variants_from_model(model, data)
            logging.info('Saving variants...')
            variants_ids = set()
            for unique_id, variant_def in variants.items():
                if unique_id in old_id_set:
                    update_variant(
                        data=data,
                        unique_id=unique_id,
                        combos_that_generated=variant_def.of_ids,
                        combos_included=variant_def.included_ids,
                        features=variant_def.feature_ids,
                        ok=is_variant_valid(variant_check_model, variant_def.card_ids),
                        restore=unique_id in to_restore)
                else:
                    variants_ids.add(
                        create_variant(
                            data=data,
                            unique_id=unique_id,
                            cards=variant_def.card_ids,
                            combos_that_generated=variant_def.of_ids,
                            combos_included=variant_def.included_ids,
                            features=variant_def.feature_ids,
                            ok=is_variant_valid(variant_check_model, variant_def.card_ids)))
            if job is not None:
                job.variants.set(variants_ids)
        else:
            variants = dict()
        new_id_set = set(variants.keys())
        to_delete = old_id_set - new_id_set
        added = new_id_set - old_id_set
        restored = new_id_set & to_restore
        logging.info(f'Added {len(added)} new variants.')
        logging.info(f'Updated {len(restored)} variants.')
        delete_query = data.variants.filter(unique_id__in=to_delete, frozen=False)
        deleted = delete_query.count()
        delete_query.delete()
        logging.info(f'Deleted {deleted} variants...')
        logging.info('Done.')
        return len(added), len(restored), deleted
