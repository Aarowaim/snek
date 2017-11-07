import time
import random
import math

from decimal import Decimal

import pygame

from pygame.locals import *
from pygame.math import Vector2

from geometry import calculateIntersectPoint;

class Entity(object):

    def draw(self, window):  # rendering tick
        pass

    def update(self, collisions=[]):  # logic/physics tick
        pass

    def handle(self, event): # event tick
        pass


class Timer(Entity):

    def __init__(self):
        self.is_paused = False
        self.__elapsed = Decimal(0)
        self.__last = self.now()

    def now(self):
        return Decimal(time.perf_counter())

    def elapsed(self):
        now = self.now()  # avoid losing time by caching

        if not self.is_paused:
            self.__elapsed += now - self.__last
        self.__last = now
        return self.__elapsed

    def consume(self, time=None):
        if time:
            self.__elapsed -= Decimal(time)
        else:
            self.__elapsed = 0

    def clear(self, time=None):
        if time:
            self.__elapsed %= time
        else:
            self.__elapsed = 0

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

class Ecosystem(Entity):

    def __init__(self, surface, food_rate=5, food_max=20):
        self.food_rate = food_rate
        self.food_max = food_max
        self.limits = Vector2(surface.get_width(), surface.get_height())

        self.food_timer = Timer()

        self.foods = {}
        self.make_food()

    def draw(self, window):
        for f in self.foods.values():
            f.draw(window)

    def update(self, collisions=[]):
        if self.food_timer.elapsed() > self.food_rate:
            self.food_timer.consume(self.food_rate)
            self.make_food()
            
    def make_food(self):
        if len(self.foods) < self.food_max:
            point = self.randpoint()
            while (int(point.x), int(point.y)) in self.foods:
                point = self.randpoint()
            self.foods[(int(point.x), int(point.y))] = Food(point.x, point.y)

    def randpoint(self):
        return Vector2(random.randint(0, self.limits.x), random.randint(0, self.limits.x))

    def check_eaten(self, vector_point):
        new_foods = {}
        eaten = 0
        for pos, f in self.foods.items():
            if not f.is_inside(vector_point):
                new_foods[pos] = f
            else:
                eaten += math.pi * f.radius ** 2
        self.foods = new_foods
        return eaten


class Food(Entity):

    def __init__(self, x, y, radius=6):
        self.radius = radius
        self.position = Vector2(x, y)

    def draw(self, window, patterns=set()): 
        self.draw_circle(window, *self.position)

    def draw_circle(self, window, x, y):
        pygame.draw.circle(
            window.get_surface(), 
            Color('white'),
            [int(val) for val in [x, y]],
            self.radius
        )

    def is_inside(self, vector_point):
        return self.position.distance_to(vector_point) <= self.radius

    def update(self, collisions=[]):
        pass

class Snake(Entity):
    def __init__(self, surface, x, y, keys, movescale=3.5):
        self.position = Vector2(x, y)
        self.velocity = Vector2(1, 0.5)
        self.velocity.scale_to_length(2)
        self.keys = keys
        self.movescale = movescale

        self.limits = Vector2(surface.get_width(), surface.get_height())

        self.max_length = 100
        self.segments = [self.position]

    def draw(self, window):
        colors = [pygame.Color(c) for c in ['green', 'yellow', 'orange', 'red', 'violet', 'blue']]
        c_i = 0
        for i in range(len(self.segments) - 1):
            pygame.draw.circle(
                window.get_surface(), 
                colors[c_i], 
                [int(val) for val in self.segments[i]],
                5
            )
            c_i = (c_i + 1) % len(colors)
                    

    def update(self, collisions=[]):
        pressed = pygame.key.get_pressed()
        offset_x = -pressed[self.keys['left']] +pressed[self.keys['right']]

        self.velocity.rotate_ip(self.movescale * offset_x)

        next_pos = self.position + self.velocity
        if self.head().distance_to(next_pos) > 1:
            self.segments.insert(0, next_pos)

        if self.length() >= self.max_length:
            self.segments.pop()

        self.position += self.velocity

    def length(self):
        accumulator = 0
        for i in range(len(self.segments) - 1):
            accumulator += self.segments[i].distance_to(self.segments[i+1])
        return accumulator

    def head(self):
        return self.segments[0]

    # TODO: Linear Algebra
    def overlaps(self):
        s = self.segments
        if len(self.segments) > 5:
            for i in range(4, len(s) - 1):
                if calculateIntersectPoint(s[0], s[1], s[i], s[i+1]):
                    return True
        return False


class NumberDisplay(Entity):

    def __init__(self, x, y, amount=0, color='white', size=48, label='', center=False):
        self.position = Vector2(x, y)
        self.color = color
        self.size = size
        self.amount = amount
        self.label = label
        self.center = center

    def draw(self, window):
        window.set_font_size(self.size)
        window.set_font_color(self.color)

        text = self.label + str(round(self.amount, 1))
        x_pos = self.position.x
        if self.center:
            x_pos = self.position.x - window.__font__.size(text)[0] / 2

        window.draw_string(text, x_pos, self.position.y)
