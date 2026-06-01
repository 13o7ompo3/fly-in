import heapq
from typing import Dict, List, Optional, Tuple, Set
from structure import Network, Zone, Connection, ZoneType, Drone

class PathNotFoundException(Exception):
    """Raised when no valid path can be found for a drone within the turn limit."""
    pass

class TimeSpaceAStar:
    def __init__(self, network: Network, max_turns: int = 200):
        self.network = network
        self.max_turns = max_turns
        # Precompute a heuristic: shortest distance from any node to the end_hub ignoring capacities
        self.heuristic_map: Dict[str, int] = self._compute_heuristics()

    def _compute_heuristics(self) -> Dict[str, int]:
        """BFS to compute the minimum turns required to reach the end_hub from any zone."""
        heuristics: Dict[str, int] = {self.network.end_hub.name: 0}
        queue = [(self.network.end_hub, 0)]

        while queue:
            current_zone, dist = queue.pop(0)
            for conn in self.network.graph[current_zone.name]:
                neighbor = conn.get_opposite(current_zone)
                cost = 2 if neighbor.type == ZoneType.RESTRICTED else 0
                if neighbor.name not in heuristics or heuristics[neighbor.name] > cost + dist:
                    heuristics[neighbor.name] = cost + dist
                    queue.append((neighbor, cost + dist))
        return heuristics

    def _can_enter_zone(self, zone: Zone, turn: int) -> bool:
        """Check if a zone has capacity at a specific turn."""
        if zone.type == ZoneType.BLOCKED:
            return False
        if zone == self.network.end_hub or zone == self.network.start_hub:
            return True
        current_occupancy = zone.occupancy_schedule.get(turn, 0)
        return current_occupancy < zone.max_drones

    def _can_use_connection(self, conn: Connection, turn: int) -> bool:
        """Check if a connection has capacity at a specific turn."""
        current_usage = conn.link_schedule.get(turn, 0)
        return current_usage < conn.capacity
    
    def find_path(self, drone: Drone) -> bool:
        """
        Finds a Time-Space path for a single drone and reserves it.
        Returns True if successful.
        """
        start_zone = drone.current_zone
        end_zone = self.network.end_hub
        
        # Priority Queue: (f_score, turn, zone_name, current_zone, path)
        # path is a list of tuples: (turn_reached, zone_or_connection)
        open_set: List[Tuple[int, int, str, Zone, List[Tuple[int, Zone | Connection]]]] = []
        heapq.heappush(open_set, (self.heuristic_map[start_zone.name], 0, start_zone.name, start_zone, [(0, start_zone)]))
        
        # Visited set for Time-Space graph: (zone_name, turn)
        closed_set: Set[Tuple[str, int]] = set()

        while open_set:
            f_score, current_turn, _, current_zone, path = heapq.heappop(open_set)
            if current_zone == end_zone:
                self._reserve_path(drone, path)
                return True
            if (current_zone.name, current_turn) in closed_set:
                continue
            closed_set.add((current_zone.name, current_turn))

            # Option 1: Wait in the current zone
            # We can wait if we haven't exceeded max turns, and the zone isn't going to push us out
            next_turn = current_turn + 1
            if self._can_enter_zone(current_zone, next_turn):
                wait_path = path + [(next_turn, current_zone)]
                h_score = self.heuristic_map.get(current_zone.name, float('inf'))
                heapq.heappush(open_set,
                               (next_turn + h_score, next_turn,
                                current_zone.name, current_zone,
                                wait_path))
            # Option 2: Move to adjacent zones
            for conn in self.network.graph[current_zone.name]:
                neighbor = conn.get_opposite(current_zone)

                if neighbor.type == ZoneType.BLOCKED:
                    continue

                if neighbor.type == ZoneType.RESTRICTED:
                    arrival_turn = current_turn + 2
                    if (self._can_use_connection(conn, current_turn) and
                        self._can_use_connection(conn, current_turn + 1) and
                        self._can_enter_zone(neighbor, arrival_turn)):

                        move_path = list(path)
                        move_path.append((current_turn, conn))
                        move_path.append((current_turn + 1, conn))
                        move_path.append((arrival_turn, neighbor))
                        h_score = self.heuristic_map.get(neighbor.name, float('inf'))
                        heapq.heappush(open_set,
                                       (arrival_turn + h_score, arrival_turn,
                                        neighbor.name, neighbor,
                                        move_path))
                else:
                    arrival_turn = current_turn + 1
                    if (self._can_use_connection(conn, current_turn) and
                        self._can_enter_zone(neighbor, arrival_turn)):

                        move_path = list(path)
                        move_path.append((current_turn, conn))
                        move_path.append((arrival_turn, neighbor))
                        priority_bonus = 0.5 if neighbor.type == ZoneType.PRIORITY else 0
                        h_score = self.heuristic_map.get(neighbor.name, float('inf')) - priority_bonus
                        heapq.heappush(open_set,
                                       (arrival_turn + h_score, arrival_turn,
                                        neighbor.name, neighbor,
                                        move_path))
        return False

    def _reserve_path(self, drone: Drone, path: List[Tuple[int, Zone | Connection]]) -> None:
        """Applies the successful path to the network's reservation tables."""
        drone.path = path
        for turn, element in path:
            if isinstance(element, Zone):
                element.occupancy_schedule[turn] = element.occupancy_schedule.get(turn, 0) + 1
            elif isinstance(element, Connection):
                element.link_schedule[turn] = element.link_schedule.get(turn, 0) + 1

        for turn, element in path.copy():
            if isinstance(element, Connection):
                del path[path.index((turn, element))]

    def solve(self) -> None:
        """Find paths for all drones in the network."""
        for drone in self.network.drones:
            if not self.find_path(drone):
                raise PathNotFoundException(f"No valid path found for drone {drone.id} within turn limit.")