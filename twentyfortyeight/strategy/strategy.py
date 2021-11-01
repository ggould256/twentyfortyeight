"""An interface for 2048 strategy modules, and several examples of
strategies."""


class Strategy(object):
    """An abstract class for 2048 strategies.  Implementors will wish
    to override at least get_move().  A strategy will be instantiated
    once at the beginning of each games, and disposed of once the game is
    complete."""

    def name(self):
        """@return a name that can be used in printing messages about this
        strategy"""
        return self.__class__.__name__

    def get_move(self, board, score):
        """
        Given the current state of the game, return the move chosen by
        this strategy.  Subclasses must implement this method.
        """
        raise NotImplementedError(
            "Strategy subclasses must implement get_move().")

    def notify_outcome(self, board, score):
        """Optionally, subclasses may choose to be notified of the
        outcome of the game.  This is your opportunity to gloat."""
        pass
