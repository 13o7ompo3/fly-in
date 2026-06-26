import sys
from parser import Parser
from a_star import TimeSpaceAStar, PathNotFoundException
from simulation import Simulator


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            print("Usage: python main.py <map_file.txt>")
            sys.exit(1)

        map_file = sys.argv[1]

        # 1. Parse the network
        network = Parser().parse_file(map_file)

        # 2. Run the Cooperative Time-Space A* solver
        solver = TimeSpaceAStar(network)
        try:
            solver.solve()
        except PathNotFoundException as e:
            print(f"Algorithm failed to find a valid routing: {e}")
            sys.exit(1)

        # 3. Play back the visual simulation
        sim = Simulator(network)
        sim.run()
    except Exception as e:
        print(f"Error: An unexpected error occurred: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user.")
        sys.exit(0)
