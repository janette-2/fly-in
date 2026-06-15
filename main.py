import sys
from errors import Parser_Error
from parser import MapParser
from simulator import Simulation


def main() -> int:
    """Entry point for the drone simulator.

    Reads a map file, parses it, and runs the simulation.

    Returns:
        0 on success, 1 on error.
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
