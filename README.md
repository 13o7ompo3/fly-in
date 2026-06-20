*This project has been created as part of the 42 curriculum by obahya.*
# Fly-in: Autonomous Drone Routing

## Description

Fly-in is an object-oriented Python simulation that solves a **Maximum Flow over Time** problem. Its goal is **makespan minimization** — routing a fleet of drones through a graph network as efficiently as possible while respecting strict capacity limits on both zones (vertices) and connections (edges).

## Requirements

- Python 3.10+
- Strict type checking and linting are enforced throughout the project

## Instructions

### Installation
```bash
make install
```

### Execution
```bash
python3 main.py <path_to_map_file>
```
or use the provided `Makefile`:
```bash
make run MAP=<path_to_map_file>
```

### Development

| Command | Description |
|---|---|
| `make lint-strict` | Check code style and type errors |
| `make debug MAP=<path_to_map_file>` | Run the simulation in debug mode |
| `make clean` | Remove generated files |

## Map File Format

```
nb_drones: 2

start_hub: start 0 0 [color=green]
hub: waypoint1 1 0 [color=blue]
hub: waypoint2 2 0 [color=blue]
end_hub: goal 3 0 [color=red]

connection: start-waypoint1
connection: waypoint1-waypoint2
connection: waypoint2-goal
```

## Algorithm

Routing a large fleet of drones through a capacity-constrained network is a classic Maximum Flow over Time problem. Standard pathfinding algorithms such as Dijkstra or basic A* fall short here, since they only reason about spatial distance and ignore time-based capacity and traffic congestion.

To address this, Fly-in implements a **Time-Space Cooperative A\*** (CA\*) algorithm — an extension of traditional A* that searches across both spatial and temporal dimensions, so drones are routed efficiently while respecting the capacity limits of zones and connections over time.

### 1. Time-Space Graph Modeling

Rather than searching a flat 2D spatial graph, the network is expanded into a 3D time-space graph. Every `Zone` and `Connection` keeps a dynamic occupancy schedule (`occupancy_schedule` / `link_schedule`) keyed by integer turn `T`.

- **State representation** — a node in the open set is `(Zone, Turn)`, not just `Zone`.
- **Dynamic waiting** — if a destination is at capacity for turn `T+1`, the algorithm can push a `(current_zone, T+1)` state instead, letting the drone idle until the path clears rather than failing the route outright.
- **Restricted transit** — zones that take 2 turns to cross have their connection reserved for both transit turns, enforcing strict link-capacity limits.

### 2. Pseudocode

```python
open_set.push((start_hub, turn=0))

while open_set is not empty:
    current_zone, current_turn = pop_lowest_f_score(open_set)

    if current_zone == end_hub:
        commit_reservations_to_global_graph()
        return SUCCESS

    # Option 1: wait for capacity to clear
    if can_occupy(current_zone, current_turn + 1):
        open_set.push((current_zone, current_turn + 1))

    # Option 2: move to a neighboring zone
    for neighbor in current_zone.connections:
        arrival_turn = current_turn + cost(neighbor)
        if can_traverse(connection, arrival_turn) and can_occupy(neighbor, arrival_turn):
            open_set.push((neighbor, arrival_turn))
```

### 3. Reservation Commit

Once a drone reaches its destination, its full path is committed to the global graph. This keeps every subsequent pathfinding call aware of newly occupied zones and connections, preventing conflicts or over-occupancy in later turns.

## Output

The simulation logs progress to the terminal, one line per turn, with color-coded zone names based on the map's metadata:

- `D<ID>-<zone_name>` — a drone arriving at a zone.
- `D<ID>-<zone1_name>-<zone2_name>` — a drone in transit on a connection leading to a restricted zone.

### Sample Run

D1-$\textcolor{blue}{\text{waypoint1}}$\
D1-$\textcolor{blue}{\text{waypoint2}}$ D2-$\textcolor{blue}{\text{waypoint1}}$\
D1-$\textcolor{red}{\text{goal}}$ D2-$\textcolor{blue}{\text{waypoint2}}$\
D2-$\textcolor{red}{\text{goal}}$

$\textcolor{green}{\text{Simulation complete in 4 turns.}}$

## Resources

- [Maximum Flow over Time problem (Wikipedia)](https://en.wikipedia.org/wiki/Maximum_flow_problem) — overview of the problem, its formulation, and known algorithmic solutions.
- [Cooperative A* (Silver, 2005)](https://cdn.aaai.org/ojs/18726/18726-52-22369-1-10-20210928.pdf) — the original paper formalizing time-space reservations for pathfinding around moving obstacles.

## AI Usage Declaration

In accordance with project guidelines, AI was used as a collaborative tool for the following specific tasks:

1. **Architecture** — formulating the shift from a 2D spatial graph to a 3D time-space graph with dynamic reservation tables.
2. **Debugging** — diagnosing a `TypeError` caused by Python's `heapq` comparing un-orderable tuple elements during tie-breaks, which led to the `itertools.count()` tie-breaking fix.
2. **Documentation** — generating the initial draft of this README file, which was then reviewed and edited for accuracy and clarity.
