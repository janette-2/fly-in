import sys
from errors import Parser_Error
from parser import MapParser
from simulator import Simulation


def main() -> int:
    """Entry point for the fly-in drone simulator.

    Usage:
        python3 main.py <path_to_map_file.txt>

    Steps:
    1. Reads the map file path from the command line.
    2. Creates a MapParser and parses the map.
    3. Creates a Simulation (which builds the graph and finds paths).
    4. (Future) Runs the simulation turn by turn.
    5. Prints the movement output.

    Returns:
        0 on success, 1 on error (wrong arguments or parsing failure).
    """

    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: python3 main.py <maps/map_file.txt>\n")
        return 1

    map_path = sys.argv[1]
    try:
        parser = MapParser(map_path)
        data = parser.cleaned_map()
        parser.checking_data(data)
        Simulation(parser)
    except Parser_Error as e:
        print(f"{e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
    # raise SystemExit(main())  # uncomment to propagate the exit code
