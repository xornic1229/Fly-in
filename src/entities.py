from __future__ import annotations

class Game:
    def __init__(self):
        self.drones: list[Drone] = []
        self.nb_drones: int = 0
        self.nodes: dict[str, Node] = {}  #Si el nodo se llama A -> A: Node
        self.edges: dict[str, list[str]] = {}  #Si A conecta con B y C -> A: [B, C]
        self.start_node: Node|None = None
        self.end_node: Node|None = None
        self.max_link_capacity: int = 0
        self.turn: int = 0
        self.total_moves: int = 0
        self.finished: bool = False

class Drone:
    def __init__(self,id: int, start_node: Node):
        self.id: int = id
        self.current_node: Node = start_node
        self.arrived: bool = False
        self.path: list[str] = []  #Lista de nodos por los que el drone ha pasado

class Node:
    def __init__(self, name : str, x: int, y: int, zone_type: str, color:str,capacity: int,edges: list[str]):
        self.name: str = name
        self.x: int = x
        self.y: int = y
        self.zone_type: str = zone_type
        self.color: str = color
        self.capacity: int = capacity
        self.edges: list[str] = edges
        self.current_drones: list[Drone] = []
 
