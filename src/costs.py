from __future__ import annotations

from src.entities import Game, Node


def get_node_entry_cost(node: Node) -> float:
    if node.zone_type == "blocked":
        return float("inf")
    if node.zone_type == "restricted":
        return 2
    if node.zone_type == "normal":
        return 1
    if node.zone_type == "priority":
        return 1

    raise Exception(f"Error: invalid zone type '{node.zone_type}' in node '{node.name}'")


def calculate_min_cost_to_end(game: Game) -> None:
    if game.end_node is None:
        raise Exception("Error: missing end_hub")

    for node in game.nodes.values():
        node.min_cost_to_end = float("inf")

    game.end_node.min_cost_to_end = 0

    changed = True

    while changed:
        changed = False

        for node in game.nodes.values():
            if node.zone_type == "blocked":
                continue

            for edge in node.edges:
                neighbor_node: Node = edge.get_other_node(node)

                if neighbor_node.zone_type == "blocked":
                    continue

                if neighbor_node.min_cost_to_end == float("inf"):
                    continue

                new_cost = get_node_entry_cost(neighbor_node) + neighbor_node.min_cost_to_end

                if new_cost < node.min_cost_to_end:
                    node.min_cost_to_end = new_cost
                    changed = True


def check_if_map_is_viable(game: Game) -> None:
    if game.start_node is None:
        raise Exception("Error: missing start_hub")

    calculate_min_cost_to_end(game)

    if game.start_node.min_cost_to_end == float("inf"):
        raise Exception("Error: start_hub cannot reach end_hub")
