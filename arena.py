import game

from danssfmlpy import media
import requests

import argparse
import copy
import random
import time

parser = argparse.ArgumentParser()
parser.add_argument('--port-player-1', '-p1', type=int, default=8000)
parser.add_argument('--port-player-2', '-p2', type=int, default=8001)
args = parser.parse_args()

media.init(640, 480, 'Yahtzee AI Arena')
media.clear(color=(0, 0, 0))

game_number = 0

class Player:
    def __init__(self, number, port):
        self.number = number
        self.port = port
        attributes = requests.get(self.url('/attributes')).json()
        self.name = attributes['name']
        color = attributes['color']
        self.color = (color['r'], color['g'], color['b'])
        self.points = 0

    def url(self, path):
        return f'http://localhost:{self.port}{path}'

    def post(self, path, json={}):
        try:
            return requests.post(self.url(path), json=json, timeout=0.02).json()
        except:
            print(f'Bad response from player {self.name}!')
            raise

    def start_new_game(self):
        self.decisions = None
        self.categories = { i: None for i in game.categories }
        self.yahtzee_bonus = 0
        self.new_game = True

    def play(self, stage, opponent):
        decisions = self.post('/play', json={
            'stage': stage,
            'dice': self.dice.roll(),
            'opponent': opponent,
            'new_game': self.new_game,
        })
        self.decisions.append(decisions)
        self.new_game = False
        if 'category' in decisions:
            if decisions['category'] not in self.categories:
                raise Exception(f'''Player {self.name} tried to score in invalid category {decisions['category']}!''')
            if self.categories[decisions['category']] != None:
                raise Exception(f'''Player {self.name} tried to score in already-chosen category {decisions['category']}!''')
            self.categories[decisions['category']] = copy.deepcopy(self.dice)
            return decisions['category']
        else:
            for die in self.dice: die.unsave()
            try:
                assert len(decisions['save_dice']) <= 5
                for i in decisions['save_dice']: self.dice[i].save()
            except:
                print(f'Player {self.name} gave bad dice-saving instructions!')
                raise
        if stage == 3: raise Exception(f'Player {self.name} did not declare a category!')

    def take_turn(self, opponent):
        self.decisions = []
        opponent_state = opponent.get_state()
        self.dice = game.Dice()
        for stage in range(1, 4):
            category = self.play(stage, opponent_state)
            if category: break
        yahtzee_bonus = (self.dice.score_yahtzee()
            and self.categories['yahtzee']
            and self.categories['yahtzee'].score_yahtzee())
        if yahtzee_bonus: self.yahtzee_bonus += 100
        self.draw_bar(category, yahtzee_bonus)

    def get_state(self):
        return {
            'categories': {category: dice.values() for category, dice in self.categories.items() if dice},
            'yahtzee_bonus': self.yahtzee_bonus,
            'decisions': self.decisions,
        }

    def get_score(self):
        score = 0
        for category, dice in self.categories.items():
            score += dice.score(category)
        return score

    def draw_bar(self, category, yahtzee_bonus):
        score = self.categories[category].score(category)
        w_game = media.width() // 10
        h_game = media.height() // 10
        x_game = w_game * (game_number // 10)
        y_game = h_game * (game_number % 10)
        h_category = h_game // 13
        w_category = w_game * score // (2 * game.category_max_score[category])
        y_category = game.categories.index(category) * h_category + y_game
        if yahtzee_bonus: h_category = h_category * 3 // 2
        if self.number == 1:
            x_game += w_game
            w_category *= -1
        media.fill(x=x_game, y=y_category, w=w_category, h=h_category, color=self.color)
        media.display()

def play_game(players):
    for player in players: player.start_new_game()
    first = random.randint(0, 1)
    for i_round in range(13):
        for i_player in range(2):
            player = players[(i_player + first) % 2]
            opponent = players[(i_player + first + 1) % 2]
            player.take_turn(opponent)

def poll_events():
    while True:
        event = media.poll_event()
        if not event: break
        if event == 'q':
            media.close()
            return True

players = [Player(0, args.port_player_1), Player(1, args.port_player_2)]

while game_number < 100:
    poll_events()
    play_game(players)
    if players[0].get_score() > players[1].get_score():
        players[0].points +=2
    elif players[0].get_score() < players[1].get_score():
        players[1].points += 2
    else:
        players[0].points += 1
        players[1].points += 1
    p1_score = players[0].get_score()
    p2_score = players[1].get_score()
    p1_percent = round(100 * players[0].points / ((game_number + 1) * 2))
    p2_percent = 100 - p1_percent
    p1_stats = f'{p1_score:4}p {players[0].name} {p1_percent:3}%'
    p2_stats = f'{p2_percent:3}% {players[1].name} {p2_score:4}p'
    l = round(p1_percent / 2)
    r = 50 - l
    pictogram = '=' * l + '><' + '=' * r
    print(f'{p1_stats} {pictogram} {p2_stats}')
    game_number += 1

if players[0].points > players[1].points:
    print(f'{players[0].name} wins!')
elif players[0].points < players[1].points:
    print(f'{players[1].name} wins!')
else:
    print('Tie!')

while True:
    if poll_events(): break
    time.sleep(0.01)
