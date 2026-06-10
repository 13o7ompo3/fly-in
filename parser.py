import re
import sys
from typing import Dict, Optional
from structure import ZoneType, Zone, Connection, Drone, Network


class Parser:
    def __init__(self) -> None:
        self.network = Network()
        self.nb_drones_found = False
        self.zone_pattern = re.compile(r"^(start_hub|end_hub|hub):"
                                       r"\s+([^\s\-]+)\s+(-?\d+)\s+(-?\d+)"
                                       r"(?:\s+\[([^\]]*)\])?$")
        self.conn_pattern = re.compile(r"^connection:"
                                       r"\s+([^\s\-]+)-([^\s\-]+)"
                                       r"(?:\s+\[([^\]]*)\])?$")

    @staticmethod
    def _parse_metadata(meta_str: Optional[str]) -> Dict[str, str]:
        """Parses the optional metadata block into a dictionary."""
        meta_dict: Dict[str, str] = {}
        if not meta_str:
            return meta_dict

        # Split by spaces to get key=value pairs or standalone tags
        pairs = meta_str.split()
        for pair in pairs:
            if '=' in pair:
                key, val = pair.split('=', 1)
                meta_dict[key] = val
            else:
                raise ValueError(f"Invalid metadata entry '{pair}'. "
                                 "Expected key=value format.")
        return meta_dict

    def parse_line(self, line: str) -> None:
        """Parses a single line of the input file."""
        network = self.network

        # 1. Strip comments and whitespace
        line = line.split('#')[0].strip()
        if not line:
            return

        # 2. Parse number of drones
        if line.startswith("nb_drones:"):
            parts = line.split(":")
            if len(parts) != 2:
                raise ValueError("Invalid nb_drones format.")
            count = int(parts[1].strip())
            if count <= 0:
                raise ValueError("nb_drones must be a positive integer.")
            for i in range(1, count + 1):
                network.drones.append(Drone(f"D{i}"))
            if self.nb_drones_found:
                raise ValueError("Multiple nb_drones definitions found.")
            self.nb_drones_found = True

        # 3. Parse Zones
        elif line.startswith(("start_hub:", "end_hub:", "hub:")):
            match = self.zone_pattern.match(line)
            if not match:
                raise ValueError("Invalid zone format.")

            h_type, name, x_str, y_str, meta_str = match.groups()

            if name in network.zones:
                raise ValueError(f"Duplicate zone name '{name}'.")

            x, y = int(x_str), int(y_str)

            # Process Metadata
            meta = Parser._parse_metadata(meta_str)

            # Parse Zone Type
            z_type_str = meta.get("zone", "normal")
            try:
                z_type = ZoneType(z_type_str)
            except ValueError:
                raise ValueError(f"Invalid zone type '{z_type_str}'. "
                                 "Must be normal, blocked, restricted, "
                                 "or priority.")

            # Parse Max Drones
            max_drones = int(meta.get("max_drones", 1))
            if max_drones <= 0:
                raise ValueError("max_drones must be a positive integer.")

            color = meta.get("color", None)

            # Create and register Zone
            zone = Zone(name, x, y, z_type, max_drones, color)
            network.zones[name] = zone
            network.graph[name] = []

            if h_type == "start_hub":
                if network.start_hub is not None:
                    raise ValueError("Multiple start_hub definitions found.")
                network.start_hub = zone
            elif h_type == "end_hub":
                if network.end_hub is not None:
                    raise ValueError("Multiple end_hub definitions found.")
                network.end_hub = zone

        # 4. Parse Connections
        elif line.startswith("connection:"):
            match = self.conn_pattern.match(line)
            if not match:
                raise ValueError("Invalid connection format. "
                                 "Check for dashes in names.")

            name1, name2, meta_str = match.groups()

            if name1 not in network.zones or name2 not in network.zones:
                raise ValueError("Connection links unknown zones: "
                                 f"{name1}, {name2}.")

            # Check for duplicates (a-b is same as b-a)
            conn_id = (name1, name2) if name1 < name2 else (name2, name1)
            if conn_id in network._seen_connections:
                raise ValueError("Duplicate connection between "
                                 f"{name1} and {name2}.")
            network._seen_connections.add(conn_id)

            # Process Metadata
            meta = Parser._parse_metadata(meta_str)
            capacity = int(meta.get("max_link_capacity", 1))
            if capacity <= 0:
                raise ValueError("max_link_capacity must be a "
                                 "positive integer.")

            zone_a = network.zones[name1]
            zone_b = network.zones[name2]

            conn = Connection(zone_a, zone_b, capacity)
            network.graph[name1].append(conn)
            network.graph[name2].append(conn)

        else:
            raise ValueError("Unknown directive.")

    def parse_file(self, filepath: str) -> Network:

        try:
            with open(filepath, 'r') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        self.parse_line(line)
                    except Exception as e:
                        # Catch-all for any parsing error on the current line
                        print(f"Parsing error on line {line_num}: {e}")
                        sys.exit(1)

        except FileNotFoundError:
            print(f"Error: File '{filepath}' not found.")
            sys.exit(1)

        # 5. Final Validations
        if not self.nb_drones_found:
            print("Parsing error: nb_drones was not defined.")
            sys.exit(1)
        if self.network.start_hub is None:
            print("Parsing error: Missing start_hub.")
            sys.exit(1)
        if self.network.end_hub is None:
            print("Parsing error: Missing end_hub.")
            sys.exit(1)

        # 6. Initialize drone positions
        for drone in self.network.drones:
            drone.current_zone = self.network.start_hub

        return self.network
