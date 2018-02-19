#!/usr/bin/env python

import argparse

from game.common import *
from game.game import Game
from strategy.basic import SpinnyStrategy, RandomStrategy

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--strategy', metavar='N', type=str,
        default='spinny',
        help="strategy to demonstrate, or model file to run a learned strategy")
    parser.add_argument('--output_file', metavar='FILENAME', type=str,
                        help="npz file into which to write example data")
    parser.add_argument('--verbose', action="store_true",
                        help="display game state at each move")
    parser.add_argument('--number_of_games', type=int, default=1,
                        help="number of games to run")
    args = parser.parse_args()

    strategy = None
    if args.strategy == "spinny":
        strategy = SpinnyStrategy()
    elif args.strategy == "random":
        strategy = RandomStrategy()
    else:
        from strategy.nn.nn_strategy import ModelStrategy
        strategy = ModelStrategy(args.strategy)

    for i in range(args.number_of_games):
        game = Game()
        running = True
        while running:
            turn_outcome = game.do_turn(
                strategy.get_move(game.board(), game.score()))
            if args.verbose:
                game.pretty_print()
            running = (turn_outcome != GAMEOVER)
        strategy.notify_outcome(game.board(), game.score())
        print(game.score())
