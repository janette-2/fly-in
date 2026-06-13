from errors import Parser_Error


class Connections():
    """Represents a bidirectional connection between two zones.

    Stores the connected zone names and the parsed link capacity
    from metadata.
    """

    def __init__(self, zone1: str, zone2: str,
                 metadata: str, line_n: int = 0) -> None:
        """Initializes a Connection with raw data and parses its metadata.

        Args:
            zone1: Name of the first zone.
            zone2: Name of the second zone.
            metadata: Raw metadata string (e.g. "[max_link_capacity=2]").
            line_n: Source line number for error reporting.
        """
        self.zone1 = zone1
        self.zone2 = zone2
        self.max_link_capacity = 1
        self._parser_metadata(metadata, line_n)

    def _parser_metadata(self, metadata: str, line_n: int) -> None:
        """Parses and validates the connection metadata string.

        Supported keys: max_link_capacity.
        Unknown keys are silently ignored.
        Raises Parser_Error on invalid format or values.

        Args:
            metadata: Raw metadata string.
            line_n: Source line number for error reporting.

        Raises:
            Parser_Error: If metadata syntax is invalid or
                max_link_capacity is not a positive integer.
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
