from errors import Parser_Error


class Zones():
    """Represents a zone (hub) in the drone network.

    Stores the zone's identity, coordinates, role (start/hub/end),
    and parsed metadata (zone type, color, max_drones).
    """

    def __init__(self, name: str, x: int, y: int, metadata: str,
                 role: str, line_n: int = 0) -> None:
        """Initializes a Zone with raw data and parses its metadata.

        Args:
            name: Unique zone identifier.
            x: X coordinate.
            y: Y coordinate.
            metadata: Raw metadata string (e.g. "[zone=restricted color=red]").
            role: Zone role — "start", "hub", or "end".
            line_n: Source line number for error reporting.
        """
        self.name = name
        self.x = x
        self.y = y
        self.role = role
        self.metadata = metadata
        self.zone = "normal"
        self.color = ""
        self.max_drones = 1
        self._parser_metadata(metadata, line_n)

    def _parser_metadata(self, metadata: str, line_n: int) -> None:
        """Parses and validates the zone metadata string.

        Supported keys: zone, color, max_drones.
        Unknown keys are silently ignored.
        Raises Parser_Error on invalid format or values.

        Args:
            metadata: Raw metadata string (e.g. "[zone=priority color=blue]").
            line_n: Source line number for error reporting.

        Raises:
            Parser_Error: If metadata syntax is invalid, zone type is unknown,
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
                continue
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
