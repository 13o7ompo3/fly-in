from enum import Enum
from typing import Dict, List, Optional, Set, Tuple


class ZoneType(Enum):
    """Enumeration of supported zone types."""

    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Zone:
    """Represents a node in the map.

    Attributes:
        name: Identifier string for the zone.
        x: X coordinate.
        y: Y coordinate.
        type: ZoneType classification.
        max_drones: Maximum simultaneous occupancy.
        color: Optional display color name.
        occupancy_schedule: Mapping of turn->occupancy count.
    """

    def __init__(
        self, name: str, x: int, y: int, z_type: ZoneType,
        max_drones: int, color: str = "white"
    ) -> None:
        self.name = name
        self.x = x
        self.y = y
        self.type = z_type
        self.max_drones = max_drones
        self.color = color

        # Tracks how many drones are in this zone at a specific turn.
        # {turn_number: current_occupancy_count}
        self.occupancy_schedule: Dict[int, int] = {}


class Connection:
    """Represents an edge between two `Zone` endpoints."""

    def __init__(self, zone_a: Zone, zone_b: Zone, capacity: int) -> None:
        """Initialize a connection between two zones.

        Args:
            zone_a: One endpoint of the connection.
            zone_b: The other endpoint of the connection.
            capacity: The number of drones that can use this link per turn.
        """
        self.zone_a = zone_a
        self.zone_b = zone_b
        self.capacity = capacity

        # Tracks how many drones are traversing this link at a specific turn.
        # {turn_number: current_occupancy_count}
        self.link_schedule: Dict[int, int] = {}

    def get_opposite(self, zone: Zone) -> Zone:
        """Return the opposing endpoint for `zone`.

        Args:
            zone: Known endpoint instance.

        Returns:
            The opposite `Zone` for this connection.
        """
        return self.zone_b if zone == self.zone_a else self.zone_a


class Drone:
    """Represents an autonomous agent in the simulation."""

    def __init__(self, d_id: str) -> None:
        """Initialize a drone with a unique identifier.

        Args:
            d_id: Unique string identifier for the drone.
        """
        self.id = d_id
        self.current_zone: Zone
        self.path: List[Tuple[int, Zone | Connection]] = []
        # e.g., [(1, roof1), (2, roof2)]


class Network:
    """Container for the global map, graph, and agent list."""

    def __init__(self) -> None:
        # mapping a zone name to its connections
        self.zones: Dict[str, Zone] = {}
        self.graph: Dict[str, List[Connection]] = {}
        self.start_hub: Optional[Zone] = None
        self.end_hub: Optional[Zone] = None
        self.drones: List[Drone] = []
        self._seen_connections: Set[Tuple[str, str]] = set()
        self._seen_coordinates: Set[Tuple[int, int]] = set()
