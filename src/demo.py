#!/usr/bin/env python

from rules import Game
from strategy import RandomStrategy

if __name__ == '__main__':
    game = Game()
    strategy = RandomStrategy()
    running = True
    while running:
        turn_outcome = game.do_turn(
            strategy.get_move(game._board, game._score))
        running = (turn_outcome != Game.GAMEOVER)
    print game._score
