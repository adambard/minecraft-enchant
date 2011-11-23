"""
enchant.py

Methods for picking enchantments via Minecraft's enchant algorithms.
"""
import random

ARMOR_ENCHANTS = [
        #(label, weight, levels, max_level, conflicts)
        ('protection', 10, [1, 17, 33, 49], 69,
            ['fire_protection', 'blast_protection', 'projectile_protection']),
        ('fire_protection', 5, [10, 16, 26, 34], 46, 
            ['protection', 'blast_protection', 'projectile_protection']),
        ('blast_protection', 2, [5, 11, 17, 23], 41,
            ['protection', 'fire_protection', 'projectile_protection']),
        ('projectile_protection', 5, [5, 13, 21, 29], 36,
            ['protection', 'fire_protection', 'blast_protection'])]

HEAD_ENCHANTS = ARMOR_ENCHANTS + [
        ('respiration', 2, [10, 20, 30], 60, []),
        ('aqua_affinity', 2, [1], 41, [])]

FOOT_ENCHANTS = ARMOR_ENCHANTS + [
        ('feather_fall', 5, [5, 11, 17, 23], 33, [])]

SWORD_ENCHANTS = [
        ('sharpness', 10, [1, 17, 33, 49, 65], 85,
            ['smite', 'bane_of_arthropods']),
        ('smite', 5, [5, 13, 21, 29, 37], 49,
            ['sharpness', 'bane_of_arthropods']),
        ('bane_of_arthropods', 5, [5, 13, 21, 29, 37], 49,
            ['sharpness', 'smite']),
        ('knockback', 5, [5, 25], 75, []),
        ('fire_aspect', 2, [10, 30], 80, []),
        ('looting', 2, [20, 32, 44], 94, [])]

TOOL_ENCHANTS = [
        ('efficiency', 10, [1, 16, 33, 46, 61], 111, []),
        ('silk_touch', 1, [25], 75, []),
        ('unbreaking', 5, [5, 15, 25], 75, []),
        ('fortune', 2, [20, 32, 44], 94, [])]

class InvalidCombination(Exception):
    pass

def base_enchant_level(slot, material):
    """
    Get the basic enchantment level of an item.
    
    A number between 1 and the value returned by this function is added
    to your enchantment level to get the "modified enchantment level.

    >>> base_enchant_level('tool', 'wood')
    15
    """

    if slot == 'sword' or slot == 'tool':
        if material == 'wood':
            return 15
        if material == 'stone':
            return 5
        if material == 'iron':
            return 14
        if material == 'diamond':
            return 10
        if material == 'gold':
            return 22
    elif slot == 'armor' or slot == 'head' or slot == 'feet':
        if material == 'leather':
            return 15
        if material == 'iron':
            return 9
        if material == 'diamond':
            return 10
        if material == 'gold':
            return 25

    raise InvalidCombination

def pick_modified_enchant_level(enchant_level, slot, material):
    """
    Get your modified enchant level, given the type of item and the enchant levels you're 
    using for this enchantment.
    """
    return random.randint(1, base_enchant_level(slot, material)) + enchant_level

def pick_enchant_fn(slot):
    """
    Return a function to pick an enchant, given a list
    of possibilities with weights, levels and conflict information.
    """
    if slot == 'tool':
        base_enchant_set = TOOL_ENCHANTS
    elif slot == 'sword':
        base_enchant_set = SWORD_ENCHANTS
    elif slot == 'armor':
        base_enchant_set = ARMOR_ENCHANTS
    elif slot == 'head':
        base_enchant_set = HEAD_ENCHANTS
    elif slot == 'feet':
        base_enchant_set = FOOT_ENCHANTS

    def pick_enchants(level, conflicts=[]):
        """
        Pick one or more enchants at random that meet the (modified) level criterium, and don't
        conflict with any of the provided conflicting enchants.
        """
        choices = [e for e in base_enchant_set if e[0] not in conflicts and e[2][0] <= level and e[3] >= level]

        # There might be no choices. If so, no enchant.
        if len(choices) == 0:
            return []

        # Build a weighted list of choices (1 entry per weight)
        weighted_choices = []
        for e in choices:
            for i in range(e[1]):
                weighted_choices.append(e)

        # Pick one of them
        choice = random.choice(weighted_choices)
        
        # Downgrade the level
        level = int(level / 2)

        # Maybe we want to add another enchant, hmm?
        chance_of_continuing = (level + 1) / 50.

        if random.random() <= chance_of_continuing:
            conflicts = conflicts + [choice[0]] + choice[4]
            return [choice] + pick_enchants(level, conflicts)

        return [choice]
        
    # Return the function
    return pick_enchants


def enchant_to_str(e, level):
    """
    Given an enchantment tuple and a modified enchantment level, figure out
    what level will be applied and return a string identifying the enchantment.
    """
    best_ench = 1
    for i, l in enumerate(e[2]):
        if level >= l:
            best_ench = i + 1
    return '{0} {1}'.format(e[0].upper(), best_ench)
