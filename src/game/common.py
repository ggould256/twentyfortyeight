"""Common constants and utilities used throughout this module."""


# Utility function
def list_zip(*lists):
    """Zip some @p lists, returning the result as a list of lists."""
    return list(map(list, zip(*lists)))


WIDTH = 4
HEIGHT = 4
STARTING_TILES = [2, 2]
TILE_FREQ = [(2, 0.75), (4, 0.25)]
PRETTY_PRINT = {0: ' ', 2: '2', 4: '4', 8: '8',
                16: 'A', 32: 'B', 64: 'C', 128: 'D',
                256: 'E', 512: 'F', 1024: 'G',
                2048: 'H', 4096: 'I', 8192: 'J'}

# Allowable moves
DIRECTIONS = UP, LEFT, DOWN, RIGHT = range(4)
PRETTY_DIRECTION = ["UP", "LEFT", "DOWN", "RIGHT"]

# Turn outcomes
TURN_OUTCOMES = OK, ILLEGAL, GAMEOVER = range(3)
