#!/usr/bin/env python

from game.common import *
from game.game import Game
import strategy.basic

if __name__ == '__main__':
    game = Game()
    strategy = strategy.basic.SpinnyStrategy()
    running = True
    while running:
        turn_outcome = game.do_turn(
            strategy.get_move(game.board(), game.score()))
        running = (turn_outcome != GAMEOVER)
    strategy.notify_outcome(game.board(), game.score())
    print(game.score())
