from __future__ import annotations


class Game:
    def __init__(self) -> None:
        self.drones: list[Drone] = []
        self.nb_drones: int = 0
        # If node is called A -> A: Node
        self.nodes: dict[str, Node] = {}
        # If A connects with B -> (A, B): Edge
        self.edges: dict[tuple[str, str], Edge] = {}
        self.start_node: Node | None = None
        self.end_node: Node | None = None
        self.turn: int = 0
        self.total_moves: int = 0
        self.finished: bool = False
        self.drones_moved_per_turn: list[int] = []


class Drone:
    def __init__(self, id: int, start_node: Node) -> None:
        self.id: int = id
        self.current_node: Node = start_node
        self.arrived: bool = False
        # List of nodes the drone has passed through
        self.path: list[str] = [start_node.name]

        self.in_transit: bool = False
        self.turns_left_in_transit: int = 0
        self.target_node: Node | None = None
        self.transit_edge: Edge | None = None


class Edge:
    def __init__(self, node1: Node, node2: Node, capacity: int) -> None:
        self.node1: Node = node1
        self.node2: Node = node2
        self.capacity: int = capacity
        self.current_drones: list[Drone] = []

    def get_other_node(self, current_node: Node) -> Node:
        if current_node == self.node1:
            return self.node2
        if current_node == self.node2:
            return self.node1
        raise Exception(
            f"Error: node '{current_node.name}' is not part of this edge"
        )


class Node:
    def __init__(
        self,
        name: str,
        x: int,
        y: int,
        zone_type: str,
        color: str,
        capacity: int,
        edges: list[Edge],
    ) -> None:
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.capacity: int = capacity
        self.edges: list[Edge] = edges
        self.current_drones: list[Drone] = []
        self.reserved_drones: list[Drone] = []
        self.min_cost_to_end: float = float("inf")
