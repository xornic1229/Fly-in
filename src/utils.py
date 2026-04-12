from __future__ import annotations

from src.entities import Drone, Game, Node


def drone_reach_end(game: Game, drone: Drone) -> None:
    drone.arrived = True
    game.finished = all(d.arrived for d in game.drones)


def move_drone(game: Game, drone: Drone, next_node: Node) -> None:
    # Remove drone from current node
    if drone in drone.current_node.current_drones:
        drone.current_node.current_drones.remove(drone)

    # Add drone to new node
    next_node.current_drones.append(drone)

    # Update drone position
    drone.current_node = next_node

    # Add new node to drone path
    drone.path.append(next_node.name)


def is_move_valid(game: Game, drone: Drone, next_node: Node) -> bool:
    # Check that drone has not already arrived
    if drone.arrived:
        return False

    # Check that drone is not in transit
    if drone.in_transit:
        return False

    # Check that destination node is not blocked
    if next_node.zone_type == "blocked":
        return False

    # Check that connection exists with current node
    current_node = drone.current_node
    connected = False

    for edge in current_node.edges:
        if edge.get_other_node(current_node) == next_node:
            connected = True
            break

    if not connected:
        return False

    # Check that destination node is not full
    if next_node != game.start_node and next_node != game.end_node:
        if (
            len(next_node.current_drones) + len(next_node.reserved_drones)
            >= next_node.capacity
        ):
            return False

    return True
