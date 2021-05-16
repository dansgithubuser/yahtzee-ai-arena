import game
from receiver import Receiver

try:
    from danssfmlpy import media
except:
    media = None

import argparse
import copy
import json
import math
import random
import socket
import time

parser = argparse.ArgumentParser()
parser.add_argument('--port-player-1', '-p1', type=int, default=8000)
parser.add_argument('--port-player-2', '-p2', type=int, default=8001)
args = parser.parse_args()

GAMES = 100

if media:
    media.init(960, 720, 'Yahtzee AI Arena')
    media.clear(color=(0, 0, 0))
    isqrt_games = int(math.sqrt(GAMES))
    w_game = media.width() // isqrt_games
    h_game = media.height() // isqrt_games
    h_category = h_game // (len(game.categories) + 2)

game_number = 0

class Bar:
    def __init__(self, player, category, yahtzee_bonus):
        score = player.categories[category].score(category) + (100 if yahtzee_bonus else 0)
        x_game = w_game * (game_number // isqrt_games)
        y_game = h_game * (game_number % isqrt_games)
        w_category = w_game * score // 300
        i_category = game.categories.index(category)
        y_category = i_category * h_category + y_game + (h_category // 2 if i_category > 6 else 0)
        self.x = x_game + w_game // 2
        self.y = y_category
        self.w = w_category
        self.h = h_category
        self.color = player.color

if media:
    class GamePlot:
        def __init__(self):
            self.record = []
            self.vertex_buffer = media.VertexBuffer(GAMES * 2 * (len(game.categories) + 1) * 6)
            self.vertex_buffer.set_type('triangles')

        def add_result(self, player, category, yahtzee_bonus):
            self.record.append((player, category, yahtzee_bonus))
            if len(self.record) % 2 == 0:
                bar1 = Bar(*self.record[-2])
                bar2 = Bar(*self.record[-1])
                bar1.w *= -1
                self.vertex_buffer.fill(x=bar1.x, y=bar1.y, w=bar1.w, h=bar1.h, color=bar1.color)
                self.vertex_buffer.fill(x=bar2.x, y=bar2.y, w=bar2.w, h=bar2.h, color=bar2.color)
                media.clear(color=(0, 0, 0))
                self.vertex_buffer.draw()
                media.display()

        def add_upper_bonus(self, player):
            x_game = w_game * (game_number // isqrt_games)
            y_game = h_game * (game_number % isqrt_games)
            self.vertex_buffer.fill(
                x=x_game + w_game // 2,
                y=y_game,
                w=w_game * 14 // 300 * (-1 if player.first else 1),
                h=h_category * 6,
                r=player.color[0],
                g=player.color[1],
                b=player.color[2],
                a=128,
            )

    game_plot = GamePlot()

class Player:
    def __init__(self, port):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(0.05)
        self.sock.connect(('localhost', port))
        self.receiver = Receiver(self.sock)
        self.name = f'({port})'
        attributes = self.req('attributes')
        self.name = attributes['name']
        color = attributes['color']
        self.color = (color['r'], color['g'], color['b'])
        self.points = 0

    def req(self, op, body=None):
        self.sock.sendall(json.dumps({'op': op, 'body': body}).encode('utf-8') + b'\0')
        try:
            res = json.loads(self.receiver.recv().decode('utf-8'))
        except:
            print(f'Bad response from player {self.name}!')
            raise
        return res

    def start_new_game(self):
        self.turn_record = None
        self.categories = {}
        self.yahtzee_bonus = 0

    def play(self, stage, opponent):
        decisions = self.req('play', {
            'stage': stage,
            'dice': self.dice.roll(),
            'opponent': opponent,
            'new_game': len(self.categories) == 0,
        })
        self.turn_record.append({
            'dice': self.dice.values(),
            'decisions': decisions,
        })
        if 'category' in decisions:
            if decisions['category'] not in game.categories:
                raise Exception(f'''Player {self.name} tried to score in invalid category {decisions['category']}!''')
            if self.categories.get(decisions['category']):
                raise Exception(f'''Player {self.name} tried to score in already-chosen category {decisions['category']}!''')
            yahtzee_bonus = (self.dice.score_yahtzee()
                and self.categories.get('yahtzee')
                and self.categories.get('yahtzee').score_yahtzee())
            self.categories[decisions['category']] = copy.deepcopy(self.dice)
            if yahtzee_bonus: self.yahtzee_bonus += 100
            if media:
                game_plot.add_result(self, decisions['category'], yahtzee_bonus)
            return True
        elif 'save_dice' in decisions:
            for die in self.dice: die.unsave()
            try:
                assert len(decisions['save_dice']) <= 5
                for i in decisions['save_dice']: self.dice[i].save()
            except:
                print(f'Player {self.name} gave bad dice-saving instructions!')
                raise
        if stage == 3: raise Exception(f'Player {self.name} did not declare a category!')

    def take_turn(self, opponent):
        self.turn_record = []
        opponent_state = opponent.get_state()
        self.dice = game.Dice()
        for stage in range(1, 4):
            if self.play(stage, opponent_state): break

    def get_state(self):
        return {
            'categories': {category: dice.values() for category, dice in self.categories.items()},
            'yahtzee_bonus': self.yahtzee_bonus,
            'turn_record': self.turn_record,
        }

    def get_score(self):
        upper = sum(self.categories[category].score(category) for category in game.categories_upper)
        if upper >= 63:
            upper += 35
            if media: game_plot.add_upper_bonus(self)
        lower = sum(self.categories[category].score(category) for category in game.categories_lower)
        return upper + lower + self.yahtzee_bonus

def play_game(players):
    for player in players:
        player.start_new_game()
        player.first = False
    first = random.randint(0, 1)
    players[first].first = True
    for i_round in range(13):
        for i_player in range(2):
            player = players[(i_player + first) % 2]
            opponent = players[(i_player + first + 1) % 2]
            player.take_turn(opponent)

if media:
    def poll_events():
        while True:
            event = media.poll_event()
            if not event: break
            if event == 'q':
                media.close()
                return True

players = [Player(args.port_player_1), Player(args.port_player_2)]

while game_number < GAMES:
    if media: poll_events()
    play_game(players)
    p1_score = players[0].get_score()
    p2_score = players[1].get_score()
    if p1_score > p2_score:
        players[0].points +=2
    elif p1_score < p2_score:
        players[1].points += 2
    else:
        players[0].points += 1
        players[1].points += 1
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

while media:
    if poll_events(): break
    time.sleep(0.01)
    media.clear(color=(0, 0, 0))
    game_plot.vertex_buffer.draw()
    media.display()
