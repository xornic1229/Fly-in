from __future__ import annotations

from src.entities import Game, Drone, Node, Edge
from src.utils import drone_reach_end, move_drone, is_move_valid


ANSI_RESET = "\033[0m"
ANSI_COLORS = {
    "black": "\033[30m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "purple": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "gray": "\033[90m",
    "grey": "\033[90m",
}


def get_color_code(color_name: str) -> str:
    return ANSI_COLORS.get(color_name.lower(), "")


def color_text(text: str, color_name: str) -> str:
    color_code = get_color_code(color_name)

    if color_code == "":
        return text

    return f"{color_code}{text}{ANSI_RESET}"


def get_connection_name(node1: Node, node2: Node) -> str:
    return f"{node1.name}-{node2.name}"


def get_edge_between_nodes(node1: Node, node2: Node) -> Edge | None:
    for edge in node1.edges:
        if edge.get_other_node(node1) == node2:
            return edge
    return None


def is_priority_node(node: Node) -> bool:
    return node.zone_type == "priority"


def is_better_move(drone: Drone, next_node: Node) -> bool:
    return next_node.min_cost_to_end < drone.current_node.min_cost_to_end


def is_better_candidate(candidate: Node, best_node: Node) -> bool:
    if candidate.min_cost_to_end < best_node.min_cost_to_end:
        return True

    if candidate.min_cost_to_end == best_node.min_cost_to_end:
        if is_priority_node(candidate) and not is_priority_node(best_node):
            return True

    return False


def node_has_space(game: Game, node: Node) -> bool:
    if node == game.start_node or node == game.end_node:
        return True

    return len(node.current_drones) + len(node.reserved_drones) < node.capacity


def edge_has_space(edge: Edge, used_edges_this_turn: dict[Edge, int]) -> bool:
    current_turn_uses = used_edges_this_turn.get(edge, 0)
    return len(edge.current_drones) + current_turn_uses < edge.capacity


def format_node_movement(drone: Drone, node: Node) -> str:
    return color_text(f"D{drone.id}-{node.name}", node.color)


def format_connection_movement(
    drone: Drone,
    from_node: Node,
    to_node: Node,
) -> str:
    connection_name = get_connection_name(from_node, to_node)
    return color_text(f"D{drone.id}-{connection_name}", to_node.color)


def reserve_node_for_drone(node: Node, drone: Drone) -> None:
    if drone not in node.reserved_drones:
        node.reserved_drones.append(drone)


def unreserve_node_for_drone(node: Node, drone: Drone) -> None:
    if drone in node.reserved_drones:
        node.reserved_drones.remove(drone)


def get_best_next_node(
    game: Game,
    drone: Drone,
    used_edges_this_turn: dict[Edge, int],
) -> Node | None:
    current_node: Node = drone.current_node
    best_node: Node | None = None

    for edge in current_node.edges:
        next_node: Node = edge.get_other_node(current_node)

        if not is_move_valid(game, drone, next_node):
            continue

        if not is_better_move(drone, next_node):
            continue

        if not node_has_space(game, next_node):
            continue

        if not edge_has_space(edge, used_edges_this_turn):
            continue

        if best_node is None or is_better_candidate(next_node, best_node):
            best_node = next_node

    return best_node


def start_restricted_move(
    game: Game,
    drone: Drone,
    next_node: Node,
    edge: Edge,
) -> str:
    current_node = drone.current_node

    if drone in current_node.current_drones:
        current_node.current_drones.remove(drone)

    reserve_node_for_drone(next_node, drone)
    edge.current_drones.append(drone)

    drone.in_transit = True
    drone.turns_left_in_transit = 1
    drone.target_node = next_node
    drone.transit_edge = edge

    game.total_moves += 1

    return format_connection_movement(drone, current_node, next_node)


def finish_restricted_move(game: Game, drone: Drone) -> str:
    if drone.target_node is None or drone.transit_edge is None:
        raise Exception(f"Error: drone {drone.id} is in invalid transit state")

    target_node = drone.target_node
    transit_edge = drone.transit_edge

    if drone in transit_edge.current_drones:
        transit_edge.current_drones.remove(drone)

    unreserve_node_for_drone(target_node, drone)
    target_node.current_drones.append(drone)
    drone.current_node = target_node
    drone.path.append(target_node.name)

    drone.in_transit = False
    drone.turns_left_in_transit = 0
    drone.target_node = None
    drone.transit_edge = None

    game.total_moves += 1

    if target_node == game.end_node:
        drone_reach_end(game, drone)

    return format_node_movement(drone, target_node)


def move_one_drone(
    game: Game,
    drone: Drone,
    used_edges_this_turn: dict[Edge, int],
) -> str | None:
    if drone.arrived:
        return None

    if drone.in_transit:
        return finish_restricted_move(game, drone)

    next_node: Node | None = get_best_next_node(
        game,
        drone,
        used_edges_this_turn,
    )

    if next_node is None:
        return None

    edge: Edge | None = get_edge_between_nodes(drone.current_node, next_node)
    if edge is None:
        return None

    used_edges_this_turn[edge] = used_edges_this_turn.get(edge, 0) + 1

    if next_node.zone_type == "restricted":
        return start_restricted_move(game, drone, next_node, edge)

    move_drone(game, drone, next_node)
    game.total_moves += 1

    if next_node == game.end_node:
        drone_reach_end(game, drone)

    return format_node_movement(drone, next_node)


def play_one_turn(game: Game) -> None:
    used_edges_this_turn: dict[Edge, int] = {}
    movements: list[str] = []

    for drone in game.drones:
        movement: str | None = move_one_drone(
            game,
            drone,
            used_edges_this_turn,
        )

        if movement is not None:
            movements.append(movement)

    game.turn += 1
    game.drones_moved_per_turn.append(len(movements))

    if not movements:
        if not game.finished:
            raise Exception(
                "Error: simulation got stuck before all drones reached end_hub"
            )
        return

    print(
        " ".join(movements)
    )


def run_algorithm(game: Game) -> None:
    while not game.finished:
        play_one_turn(game)
