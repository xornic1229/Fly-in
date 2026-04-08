from __future__ import annotations

from src.entities import Drone, Game, Node


def drone_reach_end(game: Game, drone: Drone) -> None:
    drone.arrived = True
    game.finished = all(d.arrived for d in game.drones)


def move_drone(game: Game, drone: Drone, next_node: Node) -> None:
    # Eliminar el drone del nodo actual
    if drone in drone.current_node.current_drones:
        drone.current_node.current_drones.remove(drone)

    # Agregar el drone al nuevo nodo
    next_node.current_drones.append(drone)

    # Actualizar la posición del drone
    drone.current_node = next_node

    # Agregar el nuevo nodo al path del drone
    drone.path.append(next_node.name)


def is_move_valid(game: Game, drone: Drone, next_node: Node) -> bool:
    # Verificar que el drone no haya llegado ya
    if drone.arrived:
        return False

    # Verificar que el drone no esté en tránsito
    if drone.in_transit:
        return False

    # Verificar que el nodo de destino no esté bloqueado
    if next_node.zone_type == "blocked":
        return False

    # Verificar que exista conexión con el nodo actual
    current_node = drone.current_node
    connected = False

    for edge in current_node.edges:
        if edge.get_other_node(current_node) == next_node:
            connected = True
            break

    if not connected:
        return False

    # Verificar que el nodo de destino no esté lleno
    if next_node != game.start_node and next_node != game.end_node:
        if (
            len(next_node.current_drones) + len(next_node.reserved_drones)
            >= next_node.capacity
        ):
            return False

    return True
