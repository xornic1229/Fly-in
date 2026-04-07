from __future__ import annotations

from src.entities import Game, Drone, Node


def get_node_entry_cost(node: Node) -> int:
    if node.zone_type == "restricted":
        return 2
    if node.zone_type == "normal":
        return 1
    if node.zone_type == "priority":
        return 1
    if node.zone_type == "blocked":
        return 0

    raise Exception(f"Error: invalid zone type '{node.zone_type}' in node '{node.name}'")


def get_drone_total_path_cost(game: Game, drone: Drone) -> int:
    total_cost = 0

    for node_name in drone.path[1:]:
        node = game.nodes[node_name]
        total_cost += get_node_entry_cost(node)

    return total_cost


def get_average_turns_per_drone(game: Game) -> float:
    if game.nb_drones == 0:
        return 0.0

    return game.turn / game.nb_drones


def get_total_path_cost(game: Game) -> int:
    total_cost = 0

    for drone in game.drones:
        total_cost += get_drone_total_path_cost(game, drone)

    return total_cost


def get_average_path_cost_per_drone(game: Game) -> float:
    if game.nb_drones == 0:
        return 0.0

    return get_total_path_cost(game) / game.nb_drones


def get_total_drones_moved(game: Game) -> int:
    total_moved = 0

    for moved_in_turn in game.drones_moved_per_turn:
        total_moved += moved_in_turn

    return total_moved


def get_average_drones_moved_per_turn(game: Game) -> float:
    if game.turn == 0:
        return 0.0

    return get_total_drones_moved(game) / game.turn


def get_max_drones_moved_in_one_turn(game: Game) -> int:
    if not game.drones_moved_per_turn:
        return 0

    return max(game.drones_moved_per_turn)


def get_min_drones_moved_in_one_turn(game: Game) -> int:
    if not game.drones_moved_per_turn:
        return 0

    return min(game.drones_moved_per_turn)


def print_stats(game: Game) -> None:
    print("\n===== STATS =====")
    print(f"Total simulation turns: {game.turn}")
    print(f"Total drones: {game.nb_drones}")
    print(f"Total moves executed: {game.total_moves}")
    print(f"Total path cost: {get_total_path_cost(game)}")
    print(f"Average turns per drone: {get_average_turns_per_drone(game):.2f}")
    print(f"Average path cost per drone: {get_average_path_cost_per_drone(game):.2f}")
    print(f"Average drones moved per turn: {get_average_drones_moved_per_turn(game):.2f}")
    print(f"Max drones moved in one turn: {get_max_drones_moved_in_one_turn(game)}")
    print(f"Min drones moved in one turn: {get_min_drones_moved_in_one_turn(game)}")

    print("\nDrones moved per turn:")
    for turn_number, moved_in_turn in enumerate(game.drones_moved_per_turn, start=1):
        print(f"Turn {turn_number}: {moved_in_turn}")

    print("\nPath cost per drone:")
    for drone in game.drones:
        print(f"D{drone.id}: {get_drone_total_path_cost(game, drone)}")

    print("===== END STATS =====")
