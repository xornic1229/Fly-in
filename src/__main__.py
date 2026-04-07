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

"""Tu idea consiste en **precalcular para cada nodo el coste mínimo
 hasta `end`** (`min_cost_to_end`) teniendo en cuenta los tipos de zona,
y luego usar ese valor como una **guía local** para mover los drones: 
en cada turno, los drones se procesan **uno por uno y en orden**, y cada
uno mira sus vecinos conectados para intentar avanzar solo a un nodo que 
**mejore** su situación, es decir, que tenga un `min_cost_to_end` menor que el nodo actual;
si hay varias opciones válidas, se elige la mejor, priorizando además nodos `priority`
en caso de empate, y solo se mueve si se respetan las **capacidades del nodo y de la conexión**, 
incluyendo la lógica especial de las zonas `restricted`, que requieren **2 turnos** y ocupan
la conexión mientras el drone está en tránsito.
"""