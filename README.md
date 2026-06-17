*This project has been created as part of the 42 curriculum by obahya.*

# Fly-in: Autonomous Drone Routing

## Description
* Fly-in is an Object-Oriented Python simulation solving a Maximum Flow over Time problem. The core objective is makespan minimization—efficiently routing a fleet of drones through a graph network with strict vertex (zone) and edge (connection) capacities.

## Instructions
This project is built in Python 3.10+ and strictly enforces type safety and coding standards. A `Makefile` is provided to automate dependency management, execution, and linting.

### Installation
To install the required dependencies, run:
```bash
make install
```

### Execution
To run the simulation with a specific map, execute:
```bash
python3 main.py <path_to_map_file>
```
or use the provided `Makefile`:
```bash
make run MAP=<path_to_map_file>
```

### Development & Linting
To check for code style and type errors, run:
```bash
make lint-strict
```
To run the simulation in debug mode, execute:
```bash
make debug MAP=<path_to_map_file>
```
To clean up generated files, run:
```bash
make clean
```

## Algorithm Implementation Strategy
Routing a massive fleet of drones through a constrained network is a classic Maximum Flow over Time problem. Standard pathfinding algorithms (like Dijkstra or basic A*) are insufficient because they only evaluate spatial distances, completely ignoring time-based capacities and dynamic traffic jams.

To solve this and achieve mathematically optimal throughput, this engine employs a Time-Space Cooperative A* (CA*) algorithm. This advanced algorithm extends the traditional A* search by incorporating temporal dimensions, allowing it to account for both spatial and temporal constraints simultaneously. The CA* algorithm ensures that drones are routed efficiently while respecting the capacity limits of zones and connections, effectively minimizing the overall makespan of the fleet.

### Time-Space Graph Modeling
Instead of searching a 2D spatial graph, the network expands into a 3D Time-Space graph. Every `Zone` and `Connection` maintains a dynamic hash map representing its `occupancy_schedule` or `link_schedule` at a specific integer turn `T`.
* **State Representation:** A node in the A* open set is not just (Zone), but (Zone, Turn).
* **Dynamic Wait States:** If a destination is at capacity for Turn T+1, the algorithm can intelligently append a (Current_Zone, T+1) state, commanding the drone to idle until traffic clears, rather than failing the route.
* **Restricted Transit:** For zones costing 2 turns, the solver explicitly reserves the edge Connection for both transit turns, enforcing strict physical limits on the link capacity.

## Visual Representation
The simulation provides visual feedback through a color-coded terminal log. Each line in the output represents a single simulation turn, strictly logging drone movements in the required format: `D<ID>-<destination>`.
- `D<ID>-zone_name` for zone arrivals or `D<ID>-zone1_name-zone2_name` for edge traversals.

To make the output easy to track, destination names are dynamically highlighted using ANSI terminal colors based on the map's specific zone metadata.

## Resources
### Algorithmic & Python References

- Maximum Flow over Time: A comprehensive overview of the Maximum Flow over Time problem, its mathematical formulation, and algorithmic solutions. [Wikipedia](https://en.wikipedia.org/wiki/Maximum_flow_problem)

- Cooperative A (CA): Research and documentation on extending A* pathfinding to account for time-space reservations and moving obstacles (originally formalized by David Silver, 2005). [PDF](https://cdn.aaai.org/ojs/18726/18726-52-22369-1-10-20210928.pdf)

### AI Usage Declaration
In accordance with the project guidelines, AI was utilized as a collaborative tool during the development of this project for the following specific tasks:

1. Data Modeling & Architecture: Used AI to specifically formulating the strategy to shift from a standard 2D spatial graph to a 3D Time-Space graph with dynamic reservation tables.

2. Debugging heapq Exceptions: Utilized AI to identify and resolve a specific TypeError where Python's priority queue crashed during tuple tie-breakers, leading to the implementation of the itertools.count() tie-breaking mechanism.
