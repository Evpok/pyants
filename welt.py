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
import itertools
import functools
import signal
import asyncio
from pggraphics import Weltanschauung

class Welt:
    '''The main container.
        Allows the denizens to interact, sets the Planck time
        and is responsible for most of the interactions with the
        graphics engine.'''
    def __init__(self, graphics_provider, chronon=20, grid_res=4):
        self.items = set()
        self.dead_items = set()
        
        self.collision_dict = dict()
        self.grid_threshold = 500/grid_res
        self.grid = Gitter(grid_res, grid_res)
        
        self.graphics_provider = graphics_provider
        self.loop = asyncio.new_event_loop()
        for signame in ('SIGINT', 'SIGTERM'):
            self.loop.add_signal_handler(getattr(signal, signame),
                                    functools.partial(self.stop, signame))
        self.chronon = chronon

    def add_item(self, item):
        self.items.add(item)
        item.parent_world = self
        self.graphics_provider.add_item(item.render)
        
        self.grid.put(item, *self.grid_at(item.x, item.y))
        
    def remove_item(self, item):
        self.dead_items.add(item)
    
    def cleanup(self):
        for corpse in self.dead_items:
            self.grid.remove(corpse)
            self.graphics_provider.remove_item(corpse.render)
        self.items.difference_update(self.dead_items)
        self.dead_items = set()
        
    def tick(self):
        '''Runs at each chronon'''
        self.update_collisions()
        for denizen in frozenset(self.items):
            denizen.act()
        self.cleanup()
        self.graphics_provider.update()
        self.loop.call_later(self.chronon/1000, self.tick)
    
    def grid_at(self, x, y):
        return (int(x/self.grid_threshold), int(y/self.grid_threshold))
    
    def move(self, item, dx, dy):
        '''Move `item` from (dx, dy)'''
        x, y = item.x + dx, item.y + dy
        if not self.playground(x, y):
            raise RandGekreuztException()
        item.x, item.y = x, y
        item.render.center = (x, y)
        self.grid.put(item, *self.grid_at(item.x, item.y))
            
    def start(self):
        self.loop.call_soon(self.tick)
        self.loop.run_forever()
    
    def stop(self, signame):
        print("got signal %s: exit" % signame)
        self.loop.stop()
        
    def playground(self, x, y):
        '''Is this (x, y) point in the playground?'''
        return 0 < x < 500 and 0 < y < 500
    
    def random_coord(self):
        return (random.uniform(0,500), random.uniform(0, 500))
    
    def update_collisions(self):
        collision_dict = dict()
        for checked_item in self.items:
            collision_dict[checked_item] = set()
            for denizen in self.grid.phonebook[checked_item]:
                try:
                    if checked_item in collision_dict[denizen]:
                        collision_dict[checked_item].add(denizen)
                except KeyError:
                    if denizen is checked_item:
                        continue
                    if (checked_item.x - denizen.x)**2 + (checked_item.y - denizen.y)**2 < (checked_item.render.radius + denizen.render.radius)**2:
                        collision_dict[checked_item].add(denizen)
        self.collision_dict = collision_dict
                        
    def colliders(self, item):
        '''A frozenset of all the denizen colliding with `item`'''
        return frozenset(self.collision_dict[item])
    
    def neighbours(self, item):
        return self.grid.phonebook[item]
    
    
class Gitter:
    def __init__(self, width, height):
        self.grid = {(a,b): set() for a in range(width) for b in range(height)}
        self.phonebook = dict()
        
    def put(self, item, x, y):
        try:
            self.phonebook[item].remove(item)
        except KeyError as e:
            if item in self.phonebook:
                raise e
        self.phonebook[item] = self.grid[(x, y)]
        self.phonebook[item].add(item)
        
    def remove(self, item):
        p = self.phonebook[item]
        p.remove(item)
        del self.phonebook[item]


class RandGekreuztException(Exception):
    '''Raised whenever a denizen crosses the border.'''
    pass