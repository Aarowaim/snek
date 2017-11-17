import time
import random

from decimal import Decimal # The accurate decimal type (TM)

import uagame
import pygame

from pygame.locals import *
from pygame.math import Vector2

from objects import *


def main():

    window = uagame.Window('Snake', 800, 800)
    window.set_auto_update(False)
    game = Game(window)
    game.play()
    window.close()


class Game(object):

    def __init__(self, window, pause_time=1/60):
        pygame.key.set_repeat(20, 20)

        self.window = window
        self.pause_time = pause_time

        self.close_clicked = False
        self.continue_game = True  # whether game logic should run

        # This assignment is too small to justify decoupling collisions
        self.snake = Snake(window.get_surface(), 100, 100, {'left' : K_a, 'right' : K_d})
        self.eco = Ecosystem(window.get_surface())

        self.game_timer = Timer()
        self.time_display = NumberDisplay(
            window.get_width() / 2,
            window.get_height() - window.get_font_height() - 10,
            size=24,
            center=True
        )
        self.score_display = NumberDisplay(
            0,
            0,
            size=24,
            label='Score: '
        )

        self.entities = [
            self.time_display,
            self.score_display,
            self.snake,
            self.eco
        ]

    def draw(self):
        self.window.clear()

        for e in self.entities:
            e.draw(self.window)

        self.window.update()

    def update(self):

        for e in self.entities:
            e.update()

        self.game_logic()

    def game_logic(self):
        # Update the counter to show how long the match has been
        self.game_timer.update()
        self.time_display.amount = round(self.game_timer.elapsed(), 1)

        # increase snake's size when it eats food
        self.snake.max_length += self.eco.check_eaten(self.snake.head())

        # update player's score
        self.score_display.amount = self.snake.length()

    def play(self):

        logic_time = Timer()
        logic_step = Decimal(1/60)

        render_time = Timer()
        render_step = Decimal(self.pause_time)

        while not self.close_clicked:

            self.handle_event()

            # Catch up logic state by consuming fixed units of time
            while logic_time.elapsed() > logic_step:
                if self.continue_game:
                    self.update()
                    self.continue_game = self.decide_continue()

                logic_time.consume(logic_step)

            # Render state gets updated to meet the framerate of render_step
            if render_time.elapsed() > render_step:
                render_time.clear(render_step)
                self.draw()

            time.sleep(self.pause_time)

    def handle_event(self):
        event = pygame.event.poll()

        if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
            self.close_clicked = True

        if event.type == KEYUP and event.key == K_SPACE:
            self.snake.theme_index += 1

        if self.continue_game:
            for e in self.entities:
                e.handle(event)

    def decide_continue(self):
        x = self.snake.head().x
        y = self.snake.head().y
        return not self.snake.overlaps() and \
            0 < x and x < self.window.get_width()and \
            0 < y and y < self.window.get_height()

main()
