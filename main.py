import sys
from parser import Parser_Error, MapParser


def main():

    if (len(sys.argv) != 2):
        raise Parser_Error("Usage: python3 main.py <maps/map_file.txt>")
        sys.exit

    map_path = sys.argv[1]
    parser = MapParser(map_path)


if __name__ == "__main__":
    main()
