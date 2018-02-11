#!/usr/bin/env python3

"""A mechanism for evaluating a strategy and giving it an abstract "score"
representing how good it is at 2048 without excessive computation."""

from rules import Game


class StrategyEvaluator(object):
    NUM_RUNS = 100

    def __init__(self, strategy):
        self._strategy = strategy

    def one_run(self):
        game = Game()
        running = True
        while running:
            turn_outcome = game.do_turn(
                self._strategy.get_move(game.board(), game.score()))
            running = (turn_outcome != Game.GAMEOVER)
        self._strategy.notify_outcome(game.board(), game.score())
        return game.score()

    def evaluate(self):
        total_score = 0
        for _ in range(StrategyEvaluator.NUM_RUNS):
            total_score += self.one_run()
        return total_score / StrategyEvaluator.NUM_RUNS


if __name__ == '__main__':
    import strategy
    for strat in [strategy.RandomStrategy(),
                  strategy.SpinnyStrategy()]:
        evaluator = StrategyEvaluator(strat)
        score = evaluator.evaluate()
        print(strat.name(), score)
