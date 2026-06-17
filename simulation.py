from structure import Network, Zone, Connection, Drone
from color import Color


class Simulator:
    def __init__(self, network: Network) -> None:
        self.network = network
        # Find the absolute maximum turn reached by any drone
        self.max_turns = max(
            (drone.path[-1][0] if drone.path else 0)
            for drone in self.network.drones
        )

    def _get_entity_at_turn(self, drone: Drone, turn: int
                            ) -> Zone | Connection:
        """Retrieves exactly where a drone is at a specific turn."""
        if turn >= len(drone.path):
            turn = -1
        return drone.path[turn][1]

    def _get_colored_name(self, entity: Zone | Connection) -> str:
        """Returns the entity's name wrapped in its designated ANSI color."""
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
        """Executes the simulation turn-by-turn and prints the output."""
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
        print(Color.colored_text("\nSimulation complete in "
                                 f"{self.max_turns} turns.", ["green"]))
