import heapq
import itertools
from typing import Dict, List, Tuple, Set, TypeAlias
from structure import Network, Zone, Connection, ZoneType, Drone


class PathNotFoundException(Exception):
    """Raised when no valid time-space path exists for a drone."""


# path is a list of tuples: (turn_reached, zone_or_connection)
PathElement: TypeAlias = Zone | Connection
Path: TypeAlias = List[Tuple[int, PathElement]]

# (f_score, priority, h_score, turn, tiebreaker, curr_zone, path, reservations)
# f_score = g_score + h_score (g_score = turn, h_score = distance to goal)
HeapElement: TypeAlias = Tuple[
    int | float, int, int | float, int, int, Zone, Path, Path]


class TimeSpaceAStar:
    """Time-space A* solver for routing multiple drones.

    The implementation reserves time-indexed occupancy and link
    schedules on successful path allocation.
    """

    def __init__(self, network: Network) -> None:
        """Initialize solver and precompute heuristics.

        Args:
            network: Network model with zones and connections.
        """
        self.network = network
        # Precompute heuristic: shortest distance from any node to
        # the end_hub ignoring capacities
        self.heuristic_map: Dict[str, int] = self._compute_heuristics()

    def _compute_heuristics(self) -> Dict[str, int]:
        """Compute shortest unconstrained distance to the end hub.

        Uses a BFS over the static graph and assigns a cost of 2 when
        traversing from a restricted zone, otherwise 1.

        Returns:
            Mapping of zone name to minimal heuristic distance.
        """
        if (self.network.end_hub is None
           or self.network.end_hub.type == ZoneType.BLOCKED):
            return {}

        heuristics: Dict[str, int] = {self.network.end_hub.name: 0}
        queue = [(self.network.end_hub, 0)]

        while queue:
            current_zone, dist = queue.pop(0)
            for conn in self.network.graph[current_zone.name]:
                neighbor = conn.get_opposite(current_zone)
                if neighbor.type == ZoneType.BLOCKED:
                    continue
                cost = 2 if current_zone.type == ZoneType.RESTRICTED else 1
                if (neighbor.name not in heuristics or
                        heuristics[neighbor.name] > cost + dist):
                    heuristics[neighbor.name] = cost + dist
                    queue.append((neighbor, cost + dist))
        return heuristics

    def _can_enter_zone(self, zone: Zone, turn: int) -> bool:
        """
        Args:
            zone: Zone object to check.
            turn: Turn index to query.
        Return True if `zone` has capacity at `turn`.

        Start and end hubs are treated as unlimited.
        """
        if zone.type == ZoneType.BLOCKED:
            return False
        if (zone == self.network.end_hub or
                zone == self.network.start_hub):
            return True
        current_occupancy = zone.occupancy_schedule.get(turn, 0)
        return current_occupancy < zone.max_drones

    def _can_use_connection(self, conn: Connection, turn: int) -> bool:
        """
        Args:
            conn: Connection object to check.
            turn: Turn index to query.
        Return True if `conn` has available capacity at `turn`.
        """
        current_usage = conn.link_schedule.get(turn, 0)
        return current_usage < conn.capacity

    def find_path(self, drone: Drone) -> bool:
        """Find and reserve a time-space path for `drone`.
        Args:
            drone: Drone object to find path for.
        Returns True on success and reserves occupancy/link tables.
        """
        start_zone = drone.current_zone
        end_zone = self.network.end_hub

        # Unique sequence count for tie-breaking
        tiebreaker = itertools.count()

        open_set: List[HeapElement] = []
        start_h = self.heuristic_map.get(start_zone.name, float('inf'))
        if start_h == float('inf'):
            return False  # No valid path found
        heap_item: HeapElement = (
            start_h,
            0,
            start_h,
            0,
            next(tiebreaker),
            start_zone,
            [(0, start_zone)],  # path
            [(0, start_zone)]   # reservations
        )
        heapq.heappush(open_set, heap_item)

        # Visited set for Time-Space graph: (zone_name, turn)
        closed_set: Set[Tuple[str, int]] = set()

        while open_set:
            (_, priority, _, current_turn, _,
             current_zone, path, reservations) = (
                heapq.heappop(open_set)
            )
            if current_zone == end_zone:
                self._reserve_path(drone, path, reservations)
                return True

            if (current_zone.name, current_turn) in closed_set:
                continue
            closed_set.add((current_zone.name, current_turn))

            # Option 1: Wait in the current zone
            next_turn = current_turn + 1
            if self._can_enter_zone(current_zone, next_turn):
                wait_path = list(path)
                wait_path.append((next_turn, current_zone))
                wait_res = list(reservations)
                wait_res.append((next_turn, current_zone))
                h_score = self.heuristic_map.get(
                    current_zone.name, float('inf')
                )
                wait_priority = priority
                if current_zone.type == ZoneType.PRIORITY:
                    wait_priority -= 1
                heapq.heappush(
                    open_set,
                    (
                        next_turn + h_score,
                        wait_priority,
                        h_score,
                        next_turn,
                        next(tiebreaker),
                        current_zone,
                        wait_path,
                        wait_res
                    )
                )
            # Option 2: Move to adjacent zones
            for conn in self.network.graph[current_zone.name]:
                neighbor = conn.get_opposite(current_zone)
                if neighbor is None or neighbor.type == ZoneType.BLOCKED:
                    continue

                if neighbor.type == ZoneType.RESTRICTED:
                    arrival_turn = current_turn + 2
                    if (
                        self._can_use_connection(conn, current_turn + 1)
                        and self._can_use_connection(conn, arrival_turn)
                        and self._can_enter_zone(neighbor, arrival_turn)
                    ):

                        move_path = list(path)
                        move_path.append((current_turn + 1, conn))
                        move_path.append((arrival_turn, neighbor))

                        move_res = list(reservations)
                        move_res.append((current_turn + 1, conn))
                        move_res.append((arrival_turn, conn))
                        move_res.append((arrival_turn, neighbor))

                        h_score = self.heuristic_map.get(
                            neighbor.name, float('inf')
                        )
                        heapq.heappush(
                            open_set,
                            (
                                arrival_turn + h_score,
                                priority,
                                h_score,
                                arrival_turn,
                                next(tiebreaker),
                                neighbor,
                                move_path,
                                move_res,
                            ),
                        )
                else:
                    arrival_turn = current_turn + 1
                    if (
                        self._can_use_connection(conn, arrival_turn)
                        and self._can_enter_zone(neighbor, arrival_turn)
                    ):
                        move_path = list(path)
                        move_path.append((arrival_turn, neighbor))

                        move_res = list(reservations)
                        move_res.append((arrival_turn, conn))
                        move_res.append((arrival_turn, neighbor))

                        h_score = self.heuristic_map.get(
                            neighbor.name, float('inf')
                        )
                        move_priority = priority
                        if neighbor.type == ZoneType.PRIORITY:
                            move_priority -= 1

                        heapq.heappush(
                            open_set,
                            (
                                arrival_turn + h_score,
                                move_priority,
                                h_score,
                                arrival_turn,
                                next(tiebreaker),
                                neighbor,
                                move_path,
                                move_res,
                            ),
                        )
        return False

    def _reserve_path(
        self, drone: Drone, path: Path, reservations: Path
    ) -> None:
        """Reserve zones and links according to `reservations`
        and assign `path` to `drone`.

        Args:
            drone: Drone object to assign path to.
            path: List of tuples representing the path.
            reservations: List of tuples representing the reservations.
        """
        drone.path = path
        for turn, element in reservations:
            if isinstance(element, Zone):
                element.occupancy_schedule[turn] = (
                    element.occupancy_schedule.get(turn, 0) + 1
                )
            elif isinstance(element, Connection):
                element.link_schedule[turn] = (
                    element.link_schedule.get(turn, 0) + 1
                )

    def solve(self) -> None:
        """Compute routes for all drones, raising on failure.

        Raises:
            PathNotFoundException: If any drone cannot be routed.
        """
        for drone in self.network.drones:
            if not self.find_path(drone):
                raise PathNotFoundException(
                    f"No valid path found for drone {drone.id}."
                )
