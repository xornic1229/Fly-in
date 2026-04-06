
from __future__ import annotations

from src.entities import Game, Drone, Node


VALID_ZONE_TYPES: set[str] = {"normal", "blocked", "restricted", "priority"}


def parse_input_file(file_path: str) -> Game:
    lines: list[str] = read_input_file(file_path)
    game: Game = Game()

    if not lines:
        raise Exception("Error: input file is empty")

    game.nb_drones = parse_nb_drones(lines[0], 1)

    seen_connections: set[tuple[str, str]] = set()

    for line_number, line in enumerate(lines[1:], start=2):
        if line.startswith("start_hub:"):
            name, x, y, attributes = parse_node_line(line, line_number)
            check_node_name(name, line_number)

            if game.start_node is not None:
                raise Exception(f"Error in line {line_number}: duplicated start_hub")

            if name in game.nodes:
                raise Exception(f"Error in line {line_number}: duplicated node name '{name}'")

            node = Node(
                name,
                x,
                y,
                attributes.get("zone", "normal"),
                attributes.get("color", "none"),
                attributes.get("max_drones", 1),
                [],
            )
            game.nodes[name] = node
            game.edges[name] = []
            game.start_node = node

        elif line.startswith("end_hub:"):
            name, x, y, attributes = parse_node_line(line, line_number)
            check_node_name(name, line_number)

            if game.end_node is not None:
                raise Exception(f"Error in line {line_number}: duplicated end_hub")

            if name in game.nodes:
                raise Exception(f"Error in line {line_number}: duplicated node name '{name}'")

            node = Node(
                name,
                x,
                y,
                attributes.get("zone", "normal"),
                attributes.get("color", "none"),
                attributes.get("max_drones", 1),
                [],
            )
            game.nodes[name] = node
            game.edges[name] = []
            game.end_node = node

        elif line.startswith("hub:"):
            name, x, y, attributes = parse_node_line(line, line_number)
            check_node_name(name, line_number)

            if name in game.nodes:
                raise Exception(f"Error in line {line_number}: duplicated node name '{name}'")

            node = Node(
                name,
                x,
                y,
                attributes.get("zone", "normal"),
                attributes.get("color", "none"),
                attributes.get("max_drones", 1),
                [],
            )
            game.nodes[name] = node
            game.edges[name] = []

        elif line.startswith("connection:"):
            node1, node2, attributes = parse_connection_line(line, line_number)

            if node1 not in game.nodes:
                raise Exception(f"Error in line {line_number}: connection references undefined node '{node1}'")
            if node2 not in game.nodes:
                raise Exception(f"Error in line {line_number}: connection references undefined node '{node2}'")

            normalized_connection = tuple(sorted((node1, node2)))
            if normalized_connection in seen_connections:
                raise Exception(
                    f"Error in line {line_number}: duplicated connection '{node1}-{node2}'"
                )
            seen_connections.add(normalized_connection)

            game.edges[node1].append(node2)
            game.edges[node2].append(node1)
            game.nodes[node1].edges.append(node2)
            game.nodes[node2].edges.append(node1)

        else:
            raise Exception(f"Error in line {line_number}: invalid line format")
        
    if game.start_node is None:
        raise Exception("Error: missing start_hub")
    if game.end_node is None:
        raise Exception("Error: missing end_hub")
    
    for i in range(game.nb_drones):
        drone = Drone(i, game.start_node)
        game.drones.append(drone)
        game.start_node.current_drones.append(drone)

    return game

def parse_nb_drones(line: str, line_number: int) -> int:
    if not line.startswith("nb_drones:"):
        raise Exception(
            f"Error in line {line_number}: first line must specify number of drones, e.g. 'nb_drones: 12'"
        )

    value: str = line.split(":", 1)[1].strip()

    if not value:
        raise Exception(f"Error in line {line_number}: missing number of drones")

    try:
        nb_drones = int(value)
    except ValueError:
        raise Exception(f"Error in line {line_number}: number of drones must be an integer")

    if nb_drones <= 0:
        raise Exception(f"Error in line {line_number}: number of drones must be a positive integer")

    return nb_drones


def parse_node_line(line: str, line_number: int) -> tuple[str, int, int, dict[str, str | int]]:
    main_part, metadata_part = split_metadata(line, line_number)
    parts = main_part.split()

    if len(parts) != 4:
        raise Exception(f"Error in line {line_number}: invalid node definition")

    # start_hub:/end_hub:/hub:  name  x  y
    name: str = parts[1]

    try:
        x: int = int(parts[2])
        y: int = int(parts[3])
    except ValueError:
        raise Exception(f"Error in line {line_number}: node coordinates must be integers")

    attributes = parse_node_metadata(metadata_part, line_number)
    return name, x, y, attributes


def parse_connection_line(line: str, line_number: int) -> tuple[str, str, dict[str, str | int]]:
    main_part, metadata_part = split_metadata(line, line_number)
    parts = main_part.split()

    if len(parts) != 2:
        raise Exception(f"Error in line {line_number}: invalid connection definition")

    connection_text: str = parts[1]

    if connection_text.count("-") != 1:
        raise Exception(f"Error in line {line_number}: invalid connection syntax")

    node1, node2 = connection_text.split("-", 1)

    if not node1 or not node2:
        raise Exception(f"Error in line {line_number}: invalid connection syntax")

    attributes = parse_connection_metadata(metadata_part, line_number)
    return node1, node2, attributes


def split_metadata(line: str, line_number: int) -> tuple[str, str | None]:
    if "[" not in line and "]" not in line:
        return line.strip(), None

    if line.count("[") != 1 or line.count("]") != 1:
        raise Exception(f"Error in line {line_number}: invalid metadata block syntax")

    if line.index("[") > line.index("]"):
        raise Exception(f"Error in line {line_number}: invalid metadata block syntax")

    main_part, metadata_part = line.split("[", 1)
    metadata_part = metadata_part.strip()

    if not metadata_part.endswith("]"):
        raise Exception(f"Error in line {line_number}: invalid metadata block syntax")

    metadata_part = metadata_part[:-1].strip()

    return main_part.strip(), metadata_part


def parse_node_metadata(raw_metadata: str | None, line_number: int) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {}

    if raw_metadata is None or raw_metadata == "":
        return metadata

    for item in raw_metadata.split():
        if "=" not in item:
            raise Exception(f"Error in line {line_number}: invalid node metadata '{item}'")

        key, value = item.split("=", 1)

        if key not in {"zone", "color", "max_drones"}:
            raise Exception(f"Error in line {line_number}: invalid node metadata key '{key}'")

        if key == "zone":
            if value not in VALID_ZONE_TYPES:
                raise Exception(f"Error in line {line_number}: invalid zone type '{value}'")
            metadata[key] = value

        elif key == "max_drones":
            if not value.isdigit():
                raise Exception(f"Error in line {line_number}: max_drones must be a positive integer")
            if int(value) <= 0:
                raise Exception(f"Error in line {line_number}: max_drones must be a positive integer")
            metadata[key] = int(value)

        elif key == "color":
            if value == "" or " " in value:
                raise Exception(f"Error in line {line_number}: invalid color value")
            metadata[key] = value

    return metadata


def parse_connection_metadata(raw_metadata: str | None, line_number: int) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {}

    if raw_metadata is None or raw_metadata == "":
        return metadata

    for item in raw_metadata.split():
        if "=" not in item:
            raise Exception(f"Error in line {line_number}: invalid connection metadata '{item}'")

        key, value = item.split("=", 1)

        if key != "max_link_capacity":
            raise Exception(f"Error in line {line_number}: invalid connection metadata key '{key}'")

        if not value.isdigit():
            raise Exception(f"Error in line {line_number}: max_link_capacity must be a positive integer")
        if int(value) <= 0:
            raise Exception(f"Error in line {line_number}: max_link_capacity must be a positive integer")

        metadata[key] = int(value)

    return metadata


def check_node_name(name: str, line_number: int) -> None:
    if name == "":
        raise Exception(f"Error in line {line_number}: node name cannot be empty")
    if " " in name or "-" in name:
        raise Exception(
            f"Error in line {line_number}: node name '{name}' cannot contain spaces or dashes"
        )


def read_input_file(file_path: str) -> list[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception(f"Error: file not found -> {file_path}")

    clean_lines: list[str] = []

    for line in lines:
        line = line.strip()

        if not line:
            continue

        if line.startswith("#"):
            continue

        clean_lines.append(line)

    return clean_lines


"""
nb_drones: 12

start_hub: start 0 0 [color=green max_drones=12]
hub: gate1 1 0 [color=orange max_drones=1]
hub: gate2 2 0 [color=orange max_drones=1]
hub: gate3 3 0 [color=orange max_drones=1]
hub: waiting_area1 1 1 [color=blue max_drones=4]
hub: waiting_area2 2 1 [color=blue max_drones=4]
hub: waiting_area3 3 1 [color=blue max_drones=4]
hub: restricted_tunnel1 4 0 [zone=restricted color=red max_drones=2]
hub: restricted_tunnel2 5 0 [zone=restricted color=red max_drones=2]
hub: restricted_tunnel3 6 0 [zone=restricted color=red max_drones=2]
hub: priority_bypass1 4 1 [zone=priority color=cyan max_drones=3]
hub: priority_bypass2 5 1 [zone=priority color=cyan max_drones=3]
hub: convergence 7 0 [color=yellow max_drones=6]
hub: final_bottleneck 8 0 [color=orange max_drones=3]
end_hub: goal 9 0 [color=green max_drones=12]

# Sequential gates (major bottleneck)
connection: start-gate1 [max_link_capacity=1]
connection: gate1-gate2 [max_link_capacity=1]
connection: gate2-gate3 [max_link_capacity=1]

# Waiting areas for queue management
connection: gate1-waiting_area1
connection: gate2-waiting_area2
connection: gate3-waiting_area3
connection: waiting_area1-waiting_area2
connection: waiting_area2-waiting_area3

# Restricted tunnel path (slow but more capacity)
connection: gate3-restricted_tunnel1
connection: restricted_tunnel1-restricted_tunnel2
connection: restricted_tunnel2-restricted_tunnel3
connection: restricted_tunnel3-convergence

# Priority bypass (fast but limited capacity)
connection: waiting_area1-priority_bypass1
connection: priority_bypass1-priority_bypass2
connection: priority_bypass2-convergence

# Final challenge
connection: convergence-final_bottleneck
connection: final_bottleneck-goal

# Emergency overflow paths
connection: waiting_area3-convergence"""