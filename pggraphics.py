'''
@author: Evpok Padding <evpok.padding@gmail.com>

Copyright © 2014, Evpok Padding <evpok.padding@gmail.com>

Permission is granted to Do What The Fuck You Want To
with this document.

See the WTF Public License, Version 2 as published by Sam Hocevar
at http://www.wtfpl.net if you need more details.
'''
import pygame
import asyncio
import functools
import os
import threading
    
class Weltanschauung:
    def __init__(self):
        self.items = pygame.sprite.RenderPlain()
        pygame.display.init()
        self.screen = pygame.display.set_mode((500, 500))
        self.background = pygame.Surface((500, 500))
        self.background.fill((255, 255, 255))
        self.screen.blit(self.background, (0,0))
        pygame.display.flip()
        
    def start(self):
        pygame.display.init()
        self.update()
        
    def update(self):
        self.items.clear(self.screen, self.background)
        self.items.draw(self.screen)
        pygame.display.flip()
        
    def stop(self):
        self.loop.stop()
        pygame.display.quit()
        
    def add_item(self, item):
        self.items.add(item)
    
    def remove_item(self, item):
        self.items.remove(item)
        
    def colliders(self, item):
        ''' Sprites that collides with `item`.
            Crudely use pygame.sprite.spritecollide.
            It is absolutely not optimised and has proven to be
            too slow for our purposes.'''
        return pygame.sprite.spritecollide(item, self.items, False)
    

class Putz(pygame.sprite.Sprite):
    def __init__(self, parent, center, r, colour):
        self.radius = r
        super().__init__()
        self.colour= list(colour)
        self.image = pygame.Surface((2*r, 2*r))
        self.image.fill((255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = center
        
    @property
    def center(self):
        return self.rect.center

    @center.setter
    def center(self, value):
        self.rect.center = value
    
    @property
    def alpha(self):
        return self.colour[3]/255

    @alpha.setter
    def alpha(self, value):
        self.colour[3] = int(value*255)
        self.image.set_alpha(self.colour[3])
        
        
class Kreis(Putz):
    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)
        r = self.radius
        pygame.draw.circle(self.image, self.colour, (r, r), r)
        pygame.draw.circle(self.image, [(255-e)%255 for e in self.colour[:-1]], (r, r), r, 1)