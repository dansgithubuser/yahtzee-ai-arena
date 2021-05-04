import game

from flask import Flask, request
app = Flask(__name__)

import os
with open(os.environ['BRAIN']) as f: brain = f.read()
exec(brain)

@app.route('/attributes')
def route_attributes():
    return {
        'name': name,
        'color': color,
    }

@app.route('/play', methods=['POST'])
def route_play():
    j = request.json
    return play(
        j['stage'],
        game.Dice(j['dice']),
        j['opponent'],
        j['new_game'],
    )
