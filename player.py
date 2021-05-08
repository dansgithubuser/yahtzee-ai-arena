import game
from receiver import Receiver

import json
import os
import socket

with open(os.environ['BRAIN']) as f: brain = f.read()
exec(brain)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('localhost', int(os.environ['PORT'])))
sock.listen(5)
(sock_client, address) = sock.accept()
receiver = Receiver(sock_client)
while True:
    msg = receiver.recv()
    if msg == None: break
    msg = json.loads(msg.decode('utf-8'))
    if msg['op'] == 'attributes':
        res = {
            'name': name,
            'color': color,
        }
    elif msg['op'] == 'play':
        body = msg['body']
        res = play(
            body['stage'],
            game.Dice(body['dice']),
            body['opponent'],
            body['new_game'],
        )
    sock_client.sendall(json.dumps(res).encode('utf-8') + b'\0')
