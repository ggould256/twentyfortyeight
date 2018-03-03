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
    parser.add_argument('--summary', action="store_true",
                        help="Show score summary instead of score per game.")
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
        strategy = ModelStrategy(args.strategy, verbose_period=5000)

    total = 0
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
        if not args.summary:
            print(game.score())
        total += game.score()
        if not (i % 25):
            print("...", i, "/", args.number_of_games)
    if args.summary:
        print("Strategy %s had average score %f after %d games" %
              (args.strategy,
               (total / args.number_of_games), args.number_of_games))
