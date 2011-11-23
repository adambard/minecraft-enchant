import random
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key="asdfa-90320923h09fh3920ed0osfjka;sdkvj; q23"

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
    return random.randint(1, base_enchant_level(slot, material)) + enchant_level

def pick_enchant_fn(base_enchant_set):
    def pick_enchants(level, conflicts=[]):
        choices = [e for e in base_enchant_set if e[0] not in conflicts and e[2][0] <= level]

        if len(choices) == 0:
            return []

        weighted_choices = []
        for e in choices:
            for i in range(e[1]):
                weighted_choices.append(e)

        total_weight = sum(e[1] for e in choices)

        choice = random.choice(weighted_choices)
        chance_of_continuing = (level + 1) / 50.

        if random.random() <= chance_of_continuing:
            conflicts = conflicts + [choice[0]] + choice[4]
            return [choice] + pick_enchants(level, conflicts)

        return [choice]
    return pick_enchants


def enchant_to_str(e, level):
    best_ench = 1
    for i, l in enumerate(e[2]):
        if level >= l:
            best_ench = i + 1
    return '{0} {1}'.format(e[0].upper(), best_ench)


@app.route('/')
def index():
    return render_template('index.html', level=1)

@app.route('/result/')
def result():
    try:
        level = int(request.args.get('level', 1))
    except ValueError:
        level = 1
    slot = request.args.get('slot', 'tool')
    material = request.args.get('material', 'diamond')

    if slot == 'tool':
        pick_enchants = pick_enchant_fn(TOOL_ENCHANTS)
    elif slot == 'sword':
        pick_enchants = pick_enchant_fn(SWORD_ENCHANTS)
    elif slot == 'armor':
        pick_enchants = pick_enchant_fn(ARMOR_ENCHANTS)
    elif slot == 'head':
        pick_enchants = pick_enchant_fn(HEAD_ENCHANTS)
    elif slot == 'feet':
        pick_enchants = pick_enchant_fn(FOOT_ENCHANTS)

    try:
        l = pick_modified_enchant_level(level, slot, material)
        enchants = [enchant_to_str(e, l) for e in pick_enchants(l)]
    except InvalidCombination:
        enchants = []
        flash("Invalid combination")

    return render_template('result.html',
            slot=slot,
            material=material,
            level=level,
            enchants=enchants)

@app.route('/sword/')
def sword():
    return render_template('result.html')

@app.route('/armor/')
def armor():
    return render_template('result.html')

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
