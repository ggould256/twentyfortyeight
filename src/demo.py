#!/usr/bin/env python

import rules

if __name__ == '__main__':
    g = rules.Game()
    turn = 0
    running = True
    while running:
        running = g.do_turn(turn % 4)
        turn += 1
    print g._score
