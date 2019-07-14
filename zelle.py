'''
@author: Evpok Padding <evpok.padding@gmail.com>

Copyright © 2014, Evpok Padding <evpok.padding@gmail.com>

Permission is granted to Do What The Fuck You Want To
with this document.

See the WTF Public License, Version 2 as published by Sam Hocevar
at http://www.wtfpl.net if you need more details.
'''

import random
import math
from pggraphics import Kreis
from welt import Welt, RandGekreuztException


class Zelle:
    def __init__(self, parent_world, x=None, y=None, colour=None, render=None):
        self.parent_world = parent_world
        self.x, self.y = (x, y) if x and y else parent_world.random_coord()
        self.colour = colour if colour is not None else (random.randint(0,240), random.randint(0,240), random.randint(0,240), 255)
        self.render = render if render is not None else Kreis(self, (self.x, self.y), 5, self.colour)
        # Better done at the end of __init__ since we need self.render
        self.parent_world.add_item(self)
        
    def act(self):
        pass

    def __str__(self):
        return 'Zelle {{x: {s.x}, y: {s.y}}}'.format(s=self)


class Kinderfrau(Zelle):
    def __init__(self, *args, max_content=3, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_content = max_content
        self.content = max_content
        
    def act(self):
        super().act()
        feedables = [c for c in self.parent_world.colliders(self) if hasattr(c, 'feed')]
        for denizen in feedables:
            try:
                denizen.feed(self.content/len(feedables))
            except AttributeError:
                pass
        if feedables:
            self.content = 0
            
        if self.content < self.max_content:
            self.content += self.parent_world.chronon/1000
            self.render.alpha = self.content/5
    
    def __str__(self):
        return 'Kinderfrau {{x: {s.x}, y: {s.y}, content: {s.content}}}'.format(s=self)
    

class Bewegende_Zelle(Zelle):
     def __init__(self, *args, θ=None, v=None, θ_jitter=0.1, v_jitter=0.5, **kwargs):
        super().__init__(*args, **kwargs)
        self.θ = random.uniform(-math.pi, math.pi) if θ is None else θ
        self.θ_jitter = θ_jitter
        self.v = random.gauss(100, 0.1) if v is None else v
        self.v_jitter = v_jitter
        
     def act(self):
        super().act()
        try:
            self.parent_world.move(self, *self.step())
        except RandGekreuztException:
            self.bump()
    
     def step(self):
        self.θ = random.gauss(self.θ,self.θ_jitter) #% 2*math.pi
        self.v = abs(random.gauss(self.v, self.v_jitter))
        dx = self.v*math.cos(self.θ)*self.parent_world.chronon/1000
        dy = self.v*math.sin(self.θ)*self.parent_world.chronon/1000
        return dx, dy

     def bump(self):
        self.θ += math.pi
    
     def __str__(self):
        return 'Bewegende Zelle {{x: {s.x}, y: {s.y}, v: {s.v} px⋅ms⁻¹, θ: {s.θ}}}'.format(s=self)


class Sterbliche_Zelle(Bewegende_Zelle):
    def __init__(self, *args, life=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self._life = life
    
    def act(self):
        self.age()
        super().act()
        
    def age(self):
        self.life -= abs(random.gauss(0.1 + self.v**2/10**7,0.1)) * self.parent_world.chronon/1000
    
    def die(self):
        self.parent_world.remove_item(self)
        
    @property
    def life(self):
        return self._life

    @life.setter
    def life(self, value):
        self._life = value
        self.render.alpha = 1-math.exp(-abs(value))
        if self._life <= 0:
            self.die()

    def __str__(self):
        return 'Sterbliche Zelle {{life: {s.life}, x: {s.x}, y: {s.y}, v: {s.v} px⋅ms⁻¹, θ: {s.θ}}}'.format(s=self)


class Fruchtbar_Zelle(Sterbliche_Zelle):
    def __init__(self, *args, split_threshold=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.split_threshold =  split_threshold if split_threshold is not None else random.gauss(3, 0.5)
        
    def act(self):
        self.reproduce()
        super().act()
        
    def inherit(self):
        inherits = {'life': self.life/2.1,
                    'θ'   : self.θ, 'v'   : self.v,
                    'θ_jitter' : abs(random.gauss(self.θ_jitter, 0.05)),
                    'v_jitter' : abs(random.gauss(self.v_jitter, 0.1)),
                    'split_threshold' : abs(random.gauss(self.split_threshold, 0.5)),
                    'colour'   : self.colour}
        return inherits
    
    def reproduce(self):
        if self.life > self.split_threshold:
            child = type(self)(self.parent_world, self.x, self.y, **self.inherit())
            self.life = self.life/2.1
        

class Emse(Fruchtbar_Zelle):
    def __init__(self, *args, escaping_multiplier=5, **kwargs):
        super().__init__(*args, **kwargs)
        self.escaping_multiplier = escaping_multiplier
        self.normal_speed = self.v
        self.escaping = False
        
    def feed(self, food):
        self.life += food
        
    def step(self):
        if {d for d in self.parent_world.neighbours(self) if isinstance(d, Wespe)}:
            if not self.escaping:
                self.normal_speed, self.v = self.v, self.escaping_multiplier*self.v
                self.escaping = True
        else:
            if self.escaping:
                self.v = self.normal_speed
                self.escaping = False
        return super().step()
        
    def inherit(self):
        inherits = super().inherit()
        inherits['v'] = self.normal_speed if self.escaping else self.v
        inherits['escaping_multiplier'] = abs(random.gauss(self.escaping_multiplier, 0.1))
        return inherits

class Wespe(Fruchtbar_Zelle):
    def __init__(self, *args, eat_threshold=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.eat_threshold =  eat_threshold if eat_threshold is not None else random.gauss(5, 0.5)
        
    def act(self):
        self.eat()
        super().act()
        
    def eat(self):
        if self.life < self.eat_threshold:
            for prey in (c for c in self.parent_world.colliders(self) if isinstance(c, Emse)):
                self.life += prey.life/5
                prey.die()
        
    def age(self):
        self.life -= abs(random.gauss(0.2 + self.v**2/10**7,0.1)) * self.parent_world.chronon/1000
        
    def inherit(self):
        inherits = super().inherit()
        inherits['eat_threshold'] = abs(random.gauss(self.eat_threshold, 0.5))
        return inherits
        