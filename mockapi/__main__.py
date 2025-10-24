import sys

from mockapi.mockapi.main import cli
from mockapi.mockapi.messages import Hello


if __name__ == "__main__":
    if len(sys.argv) == 1:
        print(Hello().show())
    else:
        cli()