from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    def __init__(self, name: str, x: int, y: int, z_type: ZoneType,
                 max_drones: int, color: Optional[str] = None) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.type = z_type
        self.max_drones = max_drones
        self.color = color

        # Tracks how many drones are in this zone at a specific turn.
        # {turn_number: current_occupancy_count}
        self.occupancy_schedule: Dict[int, int] = {}

    def can_enter_at_turn(self, turn: int) -> bool:
        """O(1) check if a drone can move here at a specific turn."""
        if self.type == ZoneType.BLOCKED:
            return False
        return self.occupancy_schedule.get(turn, 0) < self.max_drones

    def __gt__(self, other: object) -> bool:
        """Defines a consistent ordering for zones in the priority queue."""
        if not isinstance(other, Zone | Connection):
            return NotImplemented
        if isinstance(other, Connection):
            return ((self.name, self.name) >
                    (other.zone_a.name, other.zone_b.name))
        return self.name > other.name


class Connection:
    def __init__(self, zone_a: Zone, zone_b: Zone, capacity: int) -> None:
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.capacity = capacity

        # Tracks how many drones are traversing this link at a specific turn.
        # {turn_number: current_occupancy_count}
        self.link_schedule: Dict[int, int] = {}

    def get_opposite(self, zone: Zone) -> Zone:
        return self.zone_b if zone == self.zone_a else self.zone_a

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Connection | Zone):
            return NotImplemented
        if isinstance(other, Zone):
            return ((self.zone_a.name, self.zone_b.name) >
                    (other.name, other.name))
        return (self.zone_a, self.zone_b) > (other.zone_a, other.zone_b)


class Drone:
    def __init__(self, d_id: str) -> None:
        self.id = d_id
        self.current_zone: Optional['Zone'] = None
        self.path: List[Tuple[int, Zone | Connection]] = []
        # e.g., [(1, roof1), (2, roof2)]


class Network:
    def __init__(self) -> None:
        # mapping a zone name to its connections
        self.zones: Dict[str, Zone] = {}
        self.graph: Dict[str, List[Connection]] = {}
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.drones: List[Drone] = []
        self._seen_connections: Set[Tuple[str, str]] = set()
