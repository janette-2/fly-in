from errors import Parser_Error


class Zones():
    """Stores one zone (hub) in the drone network.

    A zone is a node in the graph with a name, coordinates, a role
    (start / hub / end), and optional metadata (zone type, color,
    max_drones).

    Args:
        name: Unique name of the zone.
        x: X coordinate on the map grid.
        y: Y coordinate on the map grid.
        metadata: Raw text inside the brackets, or "".
        role: "start", "hub", or "end".
        line_n: Line number in the map file (for errors).
    """

    def __init__(self, name: str, x: int, y: int, metadata: str,
                 role: str, line_n: int = 0) -> None:
        """Initializes the zone and parses its metadata.

        Args:
            name: Unique name of the zone.
            x: X coordinate on the map grid.
            y: Y coordinate on the map grid.
            metadata: Raw text inside the brackets, or "".
            role: "start", "hub", or "end".
            line_n: Line number in the map file (for errors).
        """
        self.name = name
        self.x = x
        self.y = y
        self.role = role
        self.metadata = metadata
        self.zone = "normal"       # default type
        self.color = ""             # no color by default
        self.max_drones = 1         # default: only 1 drone at a time
        self._parser_metadata(metadata, line_n)

    def _parser_metadata(self, metadata: str, line_n: int) -> None:
        """Parses the bracketed metadata and sets zone attributes.

        Args:
            metadata: The raw bracket string, or "".
            line_n: Line number for error messages.

        Raises:
            Parser_Error: If the syntax is wrong, zone type is unknown,
                or max_drones is not a positive integer.
        """
        if not metadata or metadata == "[]":
            return
        clean_data = metadata[1:-1]
        if "[" in clean_data or "]" in clean_data:
            raise Parser_Error(line_n, "Nested brackets are"
                               " invalid in metadata")
        data = clean_data.split()
        categories = ["zone", "color", "max_drones"]
        for item in data:
            if "=" not in item:
                raise Parser_Error(line_n,
                                   f"Invalid metadata format: '{item}'")
            parts = item.split("=", 1)
            if len(parts) != 2:
                raise Parser_Error(line_n,
                                   f"Invalid metadata format: '{item}'")
            key, val = parts
            if key not in categories:
                continue  # Skip not defined tags
            if key == "zone":
                if val not in ["normal", "blocked", "restricted", "priority"]:
                    raise Parser_Error(line_n,
                                       f"Invalid zone type: '{val}'")
                self.zone = val
            elif key == "color":
                self.color = val
            elif key == "max_drones":
                if not val.isdigit() or int(val) <= 0:
                    raise Parser_Error(
                        line_n, f"Invalid max_drones value: '{val}'")
                self.max_drones = int(val)
