from flask import Flask, render_template, request, flash
from enchant import *

app = Flask(__name__)
application = app # For WSGI purposes
app.secret_key="asdfa-90320923h09fh3920ed0osfjka;sdkvj; q23"



def get_table_url(level, slot, material):
    if slot == 'head':
        slot = 'Helmet'
    if slot == 'feet' or slot == 'foot':
        slot = 'Boots'

    return 'http://pernsteiner.org/minecraft/enchant/leveltables/{material}_{slot}_{level}.html'.format(
        material=material.title(),
        slot=slot.title(),
        level=level)



@app.route('/')
def index():
    return render_template('index.html', level=1)

@app.route('/result/')
def result():
    try:
        level = int(request.args.get('level', 1))
    except ValueError:
        level = 1
    if level < 0:
        level = 0
    if level > 50:
        level = 50
    slot = request.args.get('slot', 'tool')
    material = request.args.get('material', 'diamond')

    pick_enchants = pick_enchant_fn(slot)

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

    return render_template('result.html',
            table_url=get_table_url(level, slot, material),
            slot=slot,
            material=material,
            level=level,
            enchants=enchants)

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
