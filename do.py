#! /usr/bin/env python3

#===== imports =====#
import argparse
import copy
import datetime
import os
import re
import subprocess
import sys
import time

#===== args =====#
parser = argparse.ArgumentParser()
parser.add_argument('player_1_brain')
parser.add_argument('player_2_brain')
args = parser.parse_args()

#===== consts =====#
DIR = os.path.dirname(os.path.realpath(__file__))

#===== setup =====#
os.chdir(DIR)

#===== helpers =====#
def blue(text):
    return '\x1b[34m' + text + '\x1b[0m'

def timestamp():
    return '{:%Y-%m-%d %H:%M:%S.%f}'.format(datetime.datetime.now())

def invoke(
    *args,
    popen=False,
    no_split=False,
    out=False,
    quiet=False,
    **kwargs,
):
    if len(args) == 1 and not no_split:
        args = args[0].split()
    if not quiet:
        print(blue('-'*40))
        print(timestamp())
        print(os.getcwd()+'$', end=' ')
        if any([re.search(r'\s', i) for i in args]):
            print()
            for i in args: print(f'\t{i} \\')
        else:
            for i, v in enumerate(args):
                if i != len(args)-1:
                    end = ' '
                else:
                    end = ';\n'
                print(v, end=end)
        if kwargs: print(kwargs)
        if popen: print('popen')
        print()
    if kwargs.get('env') != None:
        env = copy.copy(os.environ)
        env.update(kwargs['env'])
        kwargs['env'] = env
    if popen:
        return subprocess.Popen(args, **kwargs)
    else:
        if 'check' not in kwargs: kwargs['check'] = True
        if out: kwargs['capture_output'] = True
        result = subprocess.run(args, **kwargs)
        if out:
            result = result.stdout.decode('utf-8').strip()
        return result

#===== main =====#
p1 = invoke(
    'python3 player.py',
    env={'BRAIN': args.player_1_brain, 'PORT': '8000'},
    popen=True,
)
time.sleep(0.5)
p2 = invoke(
    'python3 player.py',
    env={'BRAIN': args.player_2_brain, 'PORT': '8001'},
    popen=True,
)
time.sleep(0.5)
try:
    invoke('python3 arena.py')
finally:
    p1.kill()
    p2.kill()
