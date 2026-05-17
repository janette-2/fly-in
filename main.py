import sys
from parser import Parser_Error, MapParser


def main() -> int:

    if (len(sys.argv) != 2):
        sys.stderr.write("Usage: python3 main.py <maps/map_file.txt>")
        return 1

    map_path = sys.argv[1]
    try:
        parser = MapParser(map_path)
    except Parser_Error as e:
        print(f"{e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())  # real exit number in code main()
