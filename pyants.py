'''
@author: Evpok Padding <evpok.padding@gmail.com>

Copyright © 2014, Evpok Padding <evpok.padding@gmail.com>

Permission is granted to Do What The Fuck You Want To
with this document.

See the WTF Public License, Version 2 as published by Sam Hocevar
at http://www.wtfpl.net if you need more details.
'''

import sys
import time
import random
import math
import signal
import itertools

from zelle import *
from welt import Welt
from pggraphics import Weltanschauung

def handler(signum, frame):
    print('Signal handler called with signal', signum)
    sys.exit(0)
# Set the signal handler and a 5-second alarm
signal.signal(signal.SIGTERM, handler)

def main():
    w = Weltanschauung()
    monde = Welt(w, chronon=10)

    cellules = [Emse(monde, colour=(0, 0, 255, 255)) for i in range(30)]
    guêpes = [Wespe(monde, colour=(255, 0, 0, 255)) for i in range(5)]
    nourrices = [Kinderfrau(monde, colour=(0, 255, 0, 255)) for i in range(30)]

    w.start()
    monde.start()


if __name__ == '__main__':
    main()
