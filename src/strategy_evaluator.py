#!/usr/bin/env python

"""A mechanism for evaluating a strategy and giving it an abstract "score"
representing how good it is at 2048 without excessive computation."""

from rules import Game


class StrategyEvaluator(object):
    NUM_RUNS = 100

    def __init__(self, strategy_class):
        self._strategy_class = strategy_class

    def one_run(self):
        game = Game()
        strategy = self._strategy_class()
        running = True
        while running:
            turn_outcome = game.do_turn(
                strategy.get_move(game.board(), game.score()))
            running = (turn_outcome != Game.GAMEOVER)
        strategy.notify_outcome(game.board(), game.score())
        return game.score()

    def evaluate(self):
        total_score = 0
        for _ in range(StrategyEvaluator.NUM_RUNS):
            total_score += self.one_run()
        return total_score / StrategyEvaluator.NUM_RUNS


if __name__ == '__main__':
    import strategy
    e1 = StrategyEvaluator(strategy.RandomStrategy)
    e1_score = e1.evaluate()
    print "RandomStrategy", e1_score
    e2 = StrategyEvaluator(strategy.SpinnyStrategy)
    e2_score = e2.evaluate()
    print "SpinnyStrategy", e2_score
