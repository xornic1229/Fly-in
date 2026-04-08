from __future__ import annotations

from src.entities import Game, Drone, Node, Edge


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
                raise Exception(
                    f"Error in line {line_number}: duplicated start_hub"
                )

            if name in game.nodes:
                raise Exception(
                    f"Error in line {line_number}: duplicated node name "
                    f"'{name}'"
                )

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
            game.start_node = node

        elif line.startswith("end_hub:"):
            name, x, y, attributes = parse_node_line(line, line_number)
            check_node_name(name, line_number)

            if game.end_node is not None:
                raise Exception(
                    f"Error in line {line_number}: duplicated end_hub"
                )

            if name in game.nodes:
                raise Exception(
                    f"Error in line {line_number}: duplicated node name "
                    f"'{name}'"
                )

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
            game.end_node = node

        elif line.startswith("hub:"):
            name, x, y, attributes = parse_node_line(line, line_number)
            check_node_name(name, line_number)

            if name in game.nodes:
                raise Exception(
                    f"Error in line {line_number}: duplicated node name "
                    f"'{name}'"
                )

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

        elif line.startswith("connection:"):
            node1_name, node2_name, attributes = parse_connection_line(
                line, line_number
            )

            if node1_name not in game.nodes:
                raise Exception(
                    f"Error in line {line_number}: connection references "
                    f"undefined node '{node1_name}'"
                )
            if node2_name not in game.nodes:
                raise Exception(
                    f"Error in line {line_number}: connection references "
                    f"undefined node '{node2_name}'"
                )

            normalized_connection = tuple(sorted((node1_name, node2_name)))
            if normalized_connection in seen_connections:
                raise Exception(
                    f"Error in line {line_number}: duplicated connection "
                    f"'{node1_name}-{node2_name}'"
                )
            seen_connections.add(normalized_connection)

            node1: Node = game.nodes[node1_name]
            node2: Node = game.nodes[node2_name]

            edge = Edge(
                node1,
                node2,
                attributes.get("max_link_capacity", 1),
            )

            game.edges[normalized_connection] = edge
            node1.edges.append(edge)
            node2.edges.append(edge)

        else:
            raise Exception(
                f"Error in line {line_number}: invalid line format"
            )

    if game.start_node is None:
        raise Exception("Error: missing start_hub")
    if game.end_node is None:
        raise Exception("Error: missing end_hub")

    for i in range(1, game.nb_drones + 1):
        drone = Drone(i, game.start_node)
        game.drones.append(drone)
        game.start_node.current_drones.append(drone)

    return game


def parse_nb_drones(line: str, line_number: int) -> int:
    if not line.startswith("nb_drones:"):
        raise Exception(
            f"Error in line {line_number}: first line must specify "
            "number of drones, e.g. 'nb_drones: 12'"
        )

    value: str = line.split(":", 1)[1].strip()

    if not value:
        raise Exception(
            f"Error in line {line_number}: missing number of drones"
        )

    try:
        nb_drones = int(value)
    except ValueError:
        raise Exception(
            f"Error in line {line_number}: number of drones must be "
            "an integer"
        )

    if nb_drones <= 0:
        raise Exception(
            f"Error in line {line_number}: number of drones must be "
            "a positive integer"
        )

    return nb_drones


def parse_node_line(
    line: str,
    line_number: int,
) -> tuple[
    str,
    int,
    int,
    dict[str, str | int],
]:
    main_part, metadata_part = split_metadata(line, line_number)
    parts = main_part.split()

    if len(parts) != 4:
        raise Exception(
            f"Error in line {line_number}: invalid node definition"
        )

    name: str = parts[1]

    try:
        x: int = int(parts[2])
        y: int = int(parts[3])
    except ValueError:
        raise Exception(
            f"Error in line {line_number}: node coordinates must be "
            "integers"
        )

    attributes = parse_node_metadata(metadata_part, line_number)
    return name, x, y, attributes


def parse_connection_line(
    line: str,
    line_number: int,
) -> tuple[
    str,
    str,
    dict[str, str | int],
]:
    main_part, metadata_part = split_metadata(line, line_number)
    parts = main_part.split()

    if len(parts) != 2:
        raise Exception(
            f"Error in line {line_number}: invalid connection definition"
        )

    connection_text: str = parts[1]

    if connection_text.count("-") != 1:
        raise Exception(
            f"Error in line {line_number}: invalid connection syntax"
        )

    node1, node2 = connection_text.split("-", 1)

    if not node1 or not node2:
        raise Exception(
            f"Error in line {line_number}: invalid connection syntax"
        )

    attributes = parse_connection_metadata(metadata_part, line_number)
    return node1, node2, attributes


def split_metadata(
    line: str,
    line_number: int,
) -> tuple[str, str | None]:
    if "[" not in line and "]" not in line:
        return line.strip(), None

    if line.count("[") != 1 or line.count("]") != 1:
        raise Exception(
            f"Error in line {line_number}: invalid metadata block syntax"
        )

    if line.index("[") > line.index("]"):
        raise Exception(
            f"Error in line {line_number}: invalid metadata block syntax"
        )

    main_part, metadata_part = line.split("[", 1)
    metadata_part = metadata_part.strip()

    if not metadata_part.endswith("]"):
        raise Exception(
            f"Error in line {line_number}: invalid metadata block syntax"
        )

    metadata_part = metadata_part[:-1].strip()

    return main_part.strip(), metadata_part


def parse_node_metadata(
    raw_metadata: str | None,
    line_number: int,
) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {}

    if raw_metadata is None or raw_metadata == "":
        return metadata

    for item in raw_metadata.split():
        if "=" not in item:
            raise Exception(
                f"Error in line {line_number}: invalid node metadata '{item}'"
            )

        key, value = item.split("=", 1)

        if key in metadata:
            raise Exception(
                f"Error in line {line_number}: duplicated node metadata key "
                f"'{key}'"
            )

        if key not in {"zone", "color", "max_drones"}:
            raise Exception(
                f"Error in line {line_number}: invalid node metadata key "
                f"'{key}'"
            )

        if key == "zone":
            if value not in VALID_ZONE_TYPES:
                raise Exception(
                    f"Error in line {line_number}: invalid zone type '{value}'"
                )
            metadata[key] = value

        elif key == "max_drones":
            if not value.isdigit():
                raise Exception(
                    f"Error in line {line_number}: "
                    "max_drones must be a positive integer"
                )
            if int(value) <= 0:
                raise Exception(
                    f"Error in line {line_number}: "
                    "max_drones must be a positive integer"
                )
            metadata[key] = int(value)

        elif key == "color":
            if value == "" or " " in value:
                raise Exception(
                    f"Error in line {line_number}: invalid color value"
                )
            metadata[key] = value

    return metadata


def parse_connection_metadata(
    raw_metadata: str | None,
    line_number: int,
) -> dict[str, str | int]:
    metadata: dict[str, str | int] = {}

    if raw_metadata is None or raw_metadata == "":
        return metadata

    for item in raw_metadata.split():
        if "=" not in item:
            raise Exception(
                f"Error in line {line_number}: invalid connection metadata "
                f"'{item}'"
            )

        key, value = item.split("=", 1)

        if key in metadata:
            raise Exception(
                f"Error in line {line_number}: duplicated connection "
                f"metadata key '{key}'"
            )

        if key != "max_link_capacity":
            raise Exception(
                f"Error in line {line_number}: invalid connection "
                f"metadata key '{key}'"
            )

        if not value.isdigit():
            raise Exception(
                f"Error in line {line_number}: "
                "max_link_capacity must be a positive integer"
            )
        if int(value) <= 0:
            raise Exception(
                f"Error in line {line_number}: "
                "max_link_capacity must be a positive integer"
            )

        metadata[key] = int(value)

    return metadata


def check_node_name(name: str, line_number: int) -> None:
    if name == "":
        raise Exception(
            f"Error in line {line_number}: node name cannot be empty"
        )
    if " " in name or "-" in name:
        raise Exception(
            f"Error in line {line_number}: node name '{name}' "
            "cannot contain spaces or dashes"
        )


def read_input_file(file_path: str) -> list[str]:
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        raise Exception(
            f"Error: file not found -> {file_path}"
        )

    clean_lines: list[str] = []

    for line in lines:
        line = line.split("#", 1)[0].strip()

        if not line:
            continue

        clean_lines.append(line)

    return clean_lines
