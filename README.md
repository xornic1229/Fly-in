*This project has been created as part of the 42 curriculum by jaialons.*

# Fly-in

## Description
Fly-in is a Python simulation that routes a fleet of drones from a **start hub** to an **end hub** through a network (graph) of connected zones.

The goal is to **deliver all drones in the fewest possible simulation turns** while respecting:
- Zone occupancy limits (`max_drones`)
- Connection traversal limits (`max_link_capacity`)
- Zone types and movement costs (`normal`, `priority`, `restricted`, `blocked`)
- Simultaneous movement (many drones can move in the same turn if constraints allow)

This repository includes sample maps in the `maps/` directory, ranging from easy to challenger difficulty.

## Instructions

### Requirements
- Python **3.10+**
- No external graph/pathfinding libraries are used (as required by the subject).

### Install
The project has no required runtime dependencies.
For development tooling, the subject requires `flake8` and `mypy`.

Using the Makefile:

```bash
make install
```

Or manually:

```bash
python3 -m pip install -U pip
python3 -m pip install -U flake8 mypy
```

### Run
Using the Makefile (recommended):

```bash
make run FILE=maps/easy/01_linear_path.txt
```

Or directly:

```bash
python3 -m src maps/easy/01_linear_path.txt
```

### Debug
Run with Python’s built-in debugger (`pdb`):

```bash
make debug FILE=maps/medium/03_priority_puzzle.txt
```

### Clean
Remove Python caches and temporary files:

```bash
make clean
```

### Lint (flake8 + mypy)
Mandatory linting command required by the subject:

```bash
make lint
```

Optional strict mode:

```bash
make lint-strict
```

## Input format (maps)
The simulator expects a text file describing a graph.
Comments start with `#` and are ignored.

Minimal example:

```txt
nb_drones: 5
start_hub: hub 0 0 [color=green]
end_hub: goal 10 10 [color=yellow]
hub: roof1 3 4 [zone=restricted color=red]
hub: corridorA 4 3 [zone=priority color=cyan max_drones=2]
connection: hub-roof1
connection: hub-corridorA
connection: roof1-goal
connection: corridorA-goal [max_link_capacity=2]
```

### Nodes
- `start_hub: <name> <x> <y> [metadata]`
- `end_hub: <name> <x> <y> [metadata]`
- `hub: <name> <x> <y> [metadata]`

Node metadata (optional, any order):
- `zone=<type>` (default `normal`) — one of: `normal`, `blocked`, `restricted`, `priority`
- `color=<value>` (default `none`) — any single word; used for colored output
- `max_drones=<n>` (default `1`) — capacity of the zone (start/end are special-cased)

### Connections
- `connection: <node1>-<node2> [metadata]`

Connection metadata (optional):
- `max_link_capacity=<n>` (default `1`) — max drones traversing the link simultaneously

### Parser rules (enforced)
The parser stops on the first error and reports a clear message including the line number.
Key validations include:
- First line must be `nb_drones: <positive_integer>`
- Exactly one `start_hub` and one `end_hub`
- Unique node names; names cannot contain spaces or dashes (`-`)
- Connections must reference previously-defined nodes
- Duplicate connections are rejected (`a-b` and `b-a` count as duplicates)
- Zone type must be valid (`normal`, `blocked`, `restricted`, `priority`)
- Capacity values must be positive integers

## Output format
The simulation prints one line per turn.
Each line contains all movements that occurred in that turn, space-separated.

Movement tokens follow the subject format:
- `D<ID>-<zone>` when a drone moves into a zone
- `D<ID>-<connection>` when a drone is in-flight to a `restricted` zone (multi-turn movement)

Example:

```txt
D1-roof1 D2-corridorA
D1-roof2 D2-tunnelB
D1-goal D2-goal
```

At the end, the program prints a stats block (turn count, average drones moved per turn, path costs, etc.).

## Algorithm and implementation strategy
This implementation is intentionally **simple and heuristic-driven**. It aims to move as many drones as possible each turn, while biasing moves toward lower-cost routes.

### 1) Precompute a cost-to-go heuristic
Before the simulation starts, the program computes for every node a value `min_cost_to_end`:
- This is an estimate of the cheapest remaining cost to reach `end_hub`.
- Entering a node has a cost based on its zone type:
  - `normal`: 1
  - `priority`: 1
  - `restricted`: 2
  - `blocked`: unreachable (`inf`)

The computation uses repeated relaxations over edges until no improvement occurs (a Bellman-Ford-like dynamic programming pass). This keeps the solution free of forbidden graph libraries.

### 2) Turn-by-turn greedy scheduling
For each simulation turn:
- Drones are processed **sequentially in ID order**.
- For each drone, the algorithm searches its adjacent neighbors and selects the “best” candidate move that:
  - Is connected and not `blocked`
  - Does not violate zone capacity (`max_drones`), with exceptions:
    - `start_hub` and `end_hub` are treated as unlimited-capacity
  - Does not violate link capacity (`max_link_capacity`) for the current turn
  - **Strictly improves** the heuristic (`neighbor.min_cost_to_end < current.min_cost_to_end`)

Candidate ranking:
1. Lowest `min_cost_to_end`
2. Tie-breaker: prefer `priority` nodes

If no improving valid move exists, the drone waits (is omitted from the output line).

### 3) Restricted zones (multi-turn moves)
Moving *into* a `restricted` zone requires **2 turns**:
- On turn T, the drone leaves its node and occupies the connecting edge (“in transit”).
- The destination node is **reserved** immediately; the drone must arrive on turn T+1 (it cannot wait longer on the connection).
- On arrival, the edge is freed and the drone occupies the destination node.

### 4) Deadlock/stuck detection
If during a turn **no drone moves** and not all drones have reached `end_hub`, the simulation raises an error indicating it got stuck.

### Complexity notes
Let:
- $V$ = number of nodes
- $E$ = number of edges
- $D$ = number of drones
- $\Delta$ = max degree

Then:
- Precomputation is worst-case $O(V \cdot E)$ due to repeated relaxations.
- Each simulation turn is roughly $O(D \cdot \Delta)$ to evaluate local neighbor moves.
- Total runtime depends on the number of turns until completion.

## Visual representation
If nodes define `color=<name>` metadata, movements are printed with ANSI terminal colors:
- `D<ID>-<zone>` is colored using the destination node color
- `D<ID>-<connection>` is colored using the destination node color

This makes it easier to visually track drone flow, bottlenecks, and how the algorithm prioritizes certain corridors.

## Project structure
- `src/__main__.py`: entrypoint; parses args and runs the simulation
- `src/parser.py`: input parsing + validations
- `src/entities.py`: OOP model (`Game`, `Drone`, `Node`, `Edge`)
- `src/costs.py`: cost-to-go precomputation + viability checks
- `src/algorithm.py`: turn-based scheduler + movement logic
- `src/utils.py`: movement validation/state helpers
- `src/stats.py`: end-of-run metrics
- `maps/`: example map files

## Resources

### References
- Python `runpy` / `-m` execution: https://docs.python.org/3/using/cmdline.html#cmdoption-m
- `pdb` debugger: https://docs.python.org/3/library/pdb.html
- `mypy` type checker: https://mypy.readthedocs.io/
- `flake8` linter: https://flake8.pycqa.org/

### AI usage
AI assistance was used for **documentation and tooling**:
- Drafting this repository’s root `README.md` (structure, explanations, and command examples).
- Creating/updating the `Makefile` targets to match the subject requirements.

The intent is to keep the code understandable and reviewable: you should be able to explain, test, and modify the implementation without relying on AI output.
