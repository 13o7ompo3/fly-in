from structure import Network, Zone, Connection, Drone


COLORS = {
    "red": "\033[91m",
    "darkred": "\033[31m",
    "green": "\033[92m",
    "yellow": "\033[93m",
    "gold": "\033[33m",
    "blue": "\033[94m",
    "purple": "\033[95m",
    "violet": "\033[35m",
    "gray": "\033[90m",
    "black": "\033[30m",
    "brown": "\033[33m",
    "orange": "\033[33m",
    "maroon": "\033[31m",
    "crimson": "\033[91m",
    "rainbow": "\033[36m",
    "reset": "\033[0m",
    "bold": "\033[1m"
}


class Simulator:
    def __init__(self, network: Network):
        self.network = network
        # Find the absolute maximum turn reached by any drone
        self.max_turns = max(
            (drone.path[-1][0] if drone.path else 0) for drone in self.network.drones
        )

    def _get_entity_at_turn(self, drone: Drone, turn: int) -> Zone | Connection:
        """Retrieves exactly where a drone is at a specific turn."""
    #    for t, entity in drone.path:
    #        if t == turn:
    #            return entity
    #    return drone.path[-1][1] if drone.path else drone.current_zone
        if turn >= len(drone.path):
            turn = -1
        return drone.path[turn][1]

    def _get_colored_name(self, entity: Zone | Connection) -> str:
        """Returns the entity's name wrapped in its designated ANSI color."""
        if isinstance(entity, Zone):
            name = entity.name
            color = entity.color
            return f"{COLORS.get(color, COLORS['reset'])}{name}{COLORS['reset']}"

        return f"{self._get_colored_name(entity.zone_a)}-"\
            f"{self._get_colored_name(entity.zone_b)}"

    def run(self):
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
                print(f"Turn {turn}: " + ", ".join(turn_moves))
        print(f"\n{COLORS['green']}Simulation complete in {self.max_turns} turns.{COLORS['reset']}")
