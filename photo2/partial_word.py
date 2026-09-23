"""Exact strong periods of indexed three-color observations; None is unknown.

No truth pattern, image geometry, or readability decision enters this module.
Array positions are preserved, including missing beads and unreadable colors.
"""
from __future__ import annotations

from itertools import product


def validate(observations):
    if not observations:
        raise ValueError('An indexed sequence must have positive length')
    if any(c is not None and (type(c) is not int or c not in range(3))
           for c in observations):
        raise ValueError('Colors must be integer 0/1/2 or None')


def fit_period(observations, period):
    """Return slot evidence or a first conflicting pair of original positions."""
    validate(observations)
    if type(period) is not int or not 1 <= period <= len(observations):
        raise ValueError('Period must be between 1 and sequence length')
    slots = [None] * period
    support = [[] for _ in range(period)]
    for i, color in enumerate(observations):
        if color is None:
            continue
        slot = i % period
        if slots[slot] is not None and slots[slot] != color:
            return {'period': period, 'compatible': False,
                    'witness_positions': [support[slot][0], i]}
        slots[slot] = color
        support[slot].append(i)
    return {'period': period, 'compatible': True, 'slot_colors': slots,
            'support_positions': support,
            'unsupported_slots': [j for j, c in enumerate(slots) if c is None]}


def primitive(word):
    """Shortest complete cyclic block; never simplify an unknown symbol."""
    validate(word)
    if None in word:
        raise ValueError('Primitive reduction requires a complete word')
    for p in range(1, len(word) + 1):
        if len(word) % p == 0 and all(c == word[i % p] for i, c in enumerate(word)):
            return list(word[:p])
    raise AssertionError('Full length must be a period')


def canonical(word):
    """Rotation/reversal key without color permutation or filling unknowns.

    A partial word stays at its stated length: unknowns cannot justify reduction.
    A key denotes a constraint family, not one guessed completed necklace.
    """
    validate(word)
    values = list(word) if None in word else primitive(word)
    encoded = tuple(-1 if c is None else c for c in values)
    variants = []
    for direction, base in ((1, encoded), (-1, encoded[::-1])):
        for shift in range(len(base)):
            variants.append((base[shift:] + base[:shift], direction, shift))
    key, direction, shift = min(variants)
    return {'key': list(key), 'direction': direction, 'shift': shift,
            'kind': 'partial_family' if None in values else 'complete_primitive',
            'block_length': len(values)}


def completion_summary(slots, enumerate_limit=4):
    """Retain large families symbolically; list small families up to equivalence."""
    validate(slots)
    missing = [i for i, c in enumerate(slots) if c is None]
    result = {'free_slots': missing, 'raw_completion_count': 3 ** len(missing),
              'canonical_completions': None}
    if len(missing) <= enumerate_limit:
        keys = set()
        for fill in product(range(3), repeat=len(missing)):
            word = list(slots)
            for i, c in zip(missing, fill):
                word[i] = c
            keys.add(tuple(canonical(word)['key']))
        result['canonical_completions'] = [list(k) for k in sorted(keys)]
    return result


def scan(observations, *, exact_count=None):
    """Benchmark domain 1..floor(N/2), independently flag exact whole-repeat closure.

    exact_count must be an independently known full-ring N. Omit it for a local
    patch or a photo with only an estimated count. Never filter before reporting.
    """
    validate(observations)
    if exact_count is not None and (type(exact_count) is not int or exact_count < len(observations)):
        raise ValueError('Exact total must be an integer at least the array length')
    accepted, rejected = [], []
    for p in range(1, len(observations) // 2 + 1):
        fit = fit_period(observations, p)
        fit['whole_repeat_closure'] = None if exact_count is None else exact_count % p == 0
        (accepted if fit['compatible'] else rejected).append(fit)
    return {'domain': [1, len(observations) // 2], 'exact_count': exact_count,
            'compatible': accepted, 'rejected': rejected}


def holdout(observations, start, stop, *, exact_count=None):
    """Fit frozen candidates on training positions, then evaluate held-out colors."""
    if not 0 <= start < stop <= len(observations):
        raise ValueError('Invalid held-out interval')
    train = list(observations)
    train[start:stop] = [None] * (stop - start)
    result = scan(train, exact_count=exact_count)
    rows = []
    for fit in result['compatible']:
        correct = wrong = abstained = 0
        for i in range(start, stop):
            if observations[i] is None:
                continue
            prediction = fit['slot_colors'][i % fit['period']]
            if prediction is None:
                abstained += 1
            elif prediction == observations[i]:
                correct += 1
            else:
                wrong += 1
        rows.append({'period': fit['period'], 'whole_repeat_closure': fit['whole_repeat_closure'],
                     'supported_training_slots': fit['period'] - len(fit['unsupported_slots']),
                     'correct': correct, 'wrong': wrong, 'abstained': abstained,
                     'slot_colors': fit['slot_colors']})
    return {'held_out_interval': [start, stop], 'compatible': rows,
            'rejected': result['rejected']}
