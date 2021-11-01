import os
import subprocess

def test():
    """
    Run all unittests. Equivalent to:
    `poetry run python -u -m unittest discover`
    """
    os.chdir("twentyfortyeight")
    subprocess.run(
        ['python', '-u', '-m', 'unittest', 'discover']
    )
