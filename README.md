twentyfortyeight
================

Python tools related to Gabriele Cirulli's 2048 game

The `twentyfortyeight` module contains the bulk of the python code;
 * The `game` subdir contains an implementation of the rules of the game.
 * The `strategy` subdir contains strategies (machine players) for the game.

Running
-------

This project uses the Poetry evironment manager.  The easiest way to use it
is via `poetry` commands such as:

```
poetry run test
poetry run ./demo.py --strategy spinny --number_of_games 1000 --summary
```

