from errors import Parser_Error


class Connections():
    """Stores a bidirectional link between two zones.

    A connection is an edge in the graph. It connects two zones
    and can have a metadata that limits how many drones can cross
    it in the same turn (max_link_capacity).

    The map file writes it like this:
        connection: zoneA-zoneB [max_link_capacity=3]
    """

    def __init__(self, zone1: str, zone2: str,
                 metadata: str, line_n: int = 0) -> None:
        """Creates a connection and parses its metadata.

        Args:
            zone1: Name of the first zone.
            zone2: Name of the second zone.
            metadata: Raw text inside brackets, or "".
                Example: "[max_link_capacity=2]".
            line_n: Line number in the map file (for errors).
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = 1   # default: 1 drone per turn
        self._parser_metadata(metadata, line_n)

    def _parser_metadata(self, metadata: str, line_n: int) -> None:
        """Reads the bracketed metadata and sets the link capacity.

        The metadata looks like:  [max_link_capacity=2]
        This method extracts the value and checks it is valid.

        Rules from the subject:
        - max_link_capacity must be a positive integer
        - Unknown keys are silently ignored
        - Nested brackets are not allowed

        Args:
            metadata: The raw bracket string, or "".
            line_n: Line number for error messages.

        Raises:
            Parser_Error: If the syntax is wrong or max_link_capacity
                is not a positive integer.
        """
        if not metadata or metadata == "[]":
            return
        clean_data = metadata[1:-1]
        if "[" in clean_data or "]" in clean_data:
            raise Parser_Error(line_n, "Nested brackets are "
                               "invalid in metadata")
        keys = clean_data.split()
        for category in keys:
            if "=" not in category:
                raise Parser_Error(
                    line_n, f"Invalid metadata format: '{category}'")
            data = category.split("=", 1)
            if len(data) != 2:
                raise Parser_Error(
                    line_n, f"Invalid metadata format: '{category}'")
            key, val = data
            if key == "max_link_capacity":
                if not val.isdigit() or int(val) <= 0:
                    raise Parser_Error(
                        line_n,
                        f"Invalid max_link_capacity value: '{val}'")
                self.max_link_capacity = int(val)
