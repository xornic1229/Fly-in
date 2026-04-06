import sys
import src.parser as parser
import src.entities as entities

from src.entities import Game


def main() -> None:
    if len(sys.argv) != 2:
        raise Exception("Usage: python -m src <input_file>")

    file_path = sys.argv[1]

    game: Game = parser.parse_input_file(file_path)

    # ===== DEBUG PARSER =====

    print("\n--- PARSER OUTPUT ---\n")

    print(f"Number of drones: {game.nb_drones}")

    print("\nStart node:")
    if game.start_node:
        print(f"  {game.start_node.name} ({game.start_node.x}, {game.start_node.y})")

    print("\nEnd node:")
    if game.end_node:
        print(f"  {game.end_node.name} ({game.end_node.x}, {game.end_node.y})")

    print("\nNodes:")
    for name, node in game.nodes.items():
        print(
            f"  {name} -> ({node.x}, {node.y}) "
            f"type={node.zone_type} "
            f"capacity={node.capacity} "
            f"color={node.color}"
        )

    print("\nConnections:")
    for node, neighbors in game.edges.items():
        print(f"  {node}: {neighbors}")

    print("\n--- END ---\n")


if __name__ == "__main__":
    main()