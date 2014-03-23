#!/usr/bin/env python

from rules import Game
import strategy

if __name__ == '__main__':
    game = Game()
    strategy = strategy.SpinnyStrategy()
    running = True
    while running:
        turn_outcome = game.do_turn(
            strategy.get_move(game.board(), game.score()))
        running = (turn_outcome != Game.GAMEOVER)
    strategy.notify_outcome(game.board(), game.score())
    print game.score()
