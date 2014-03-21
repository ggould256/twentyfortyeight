#!/usr/bin/env python

from rules import Game

if __name__ == '__main__':
    g = Game()
    turn = 0
    running = True
    while running:
        turn_outcome = g.do_turn(Game.DIRECTIONS[turn % len(Game.DIRECTIONS)])
        running = (turn_outcome != Game.GAMEOVER)
        turn += 1
    print g._score
