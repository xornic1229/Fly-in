import sys
import src.parser as parser

from src.entities import Game
from src.costs import check_if_map_is_viable
from src.algorithm import run_algorithm
from src.stats import print_stats


def main() -> None:
    if len(sys.argv) != 2:
        raise Exception("Usage: python -m src <input_file>")

    file_path = sys.argv[1]

    game: Game = parser.parse_input_file(file_path)
    check_if_map_is_viable(game)
    run_algorithm(game)
    print_stats(game)


if __name__ == "__main__":
    main()
