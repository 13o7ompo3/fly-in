from structure import Network, Zone, Connection, Drone
from color import Color


class Simulator:
    """Execute and render the solved drone schedules.

    The simulator expects a `Network` instance where drones have their
    `path` attribute populated by the solver.
    """

    def __init__(self, network: Network) -> None:
        """Initialize with a parsed and solved `Network`.

        Args:
            network: Parsed network with solved drone paths.
        """
        self.network = network
        # Find the absolute maximum turn reached by any drone
        self.max_turns = max(
            (drone.path[-1][0] if drone.path else 0)
            for drone in self.network.drones
        )

    def _get_entity_at_turn(
        self, drone: Drone, turn: int
    ) -> Zone | Connection:
        """Return the zone or connection where `drone` is at `turn`.

        If `turn` is beyond the provided path, the last entry is used.

        Args:
            drone: Drone object containing `path` entries.
            turn: Turn index to query.

        Returns:
            The `Zone` or `Connection` instance for that turn.
        """
        if turn >= len(drone.path):
            turn = -1
        return drone.path[turn][1]

    def _get_colored_name(self, entity: Zone | Connection) -> str:
        """Format the readable name of `entity` with ANSI colors.

        Args:
            entity: A `Zone` or `Connection` instance.

        Returns:
            A display string potentially wrapped in ANSI codes.
        """
        if isinstance(entity, Zone):
            name = entity.name
            color = entity.color if entity.color else "white"
            if color == "white":
                return name
            if color != "rainbow":
                return Color.colored_text(name, [color])
            return Color.colored_text(name, ["red", "orange", "yellow",
                                             "green", "blue", "indigo",
                                             "violet"])
        return f"{self._get_colored_name(entity.zone_a)}-"\
            f"{self._get_colored_name(entity.zone_b)}"

    def run(self) -> None:
        """Print turn-by-turn movements for all drones.

        Movement lines follow the format `DroneId-Location` and are
        printed only when a drone changes its occupied entity.
        """
        total_moves = 0
        for turn in range(1, self.max_turns + 1):
            turn_moves = []
            for drone in self.network.drones:
                prev_pos = self._get_entity_at_turn(drone, turn - 1)
                curr_pos = self._get_entity_at_turn(drone, turn)
                if prev_pos != curr_pos:
                    dest_name = self._get_colored_name(curr_pos)
                    turn_moves.append(f"{drone.id}-{dest_name}")
            if turn_moves:
                print(" ".join(turn_moves))
                total_moves += len(turn_moves)
        print(Color.colored_text("\nSimulation complete in "
                                 f"{self.max_turns} turns.", ["green"]))
        print(Color.colored_text(f"Total moves: {total_moves}", ["green"]))
        print(Color.colored_text(
            "The average number of moves per turn: "
            f"{total_moves / self.max_turns:.2f}",
            ["green"]))
        print(Color.colored_text(
            "The average number of moves per drone: "
            f"{total_moves/len(self.network.drones):.2f}",
            ["green"]))
