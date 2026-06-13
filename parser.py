from errors import Parser_Error
from zones import Zones
from connections import Connections


class MapParser():
    """Parses and validates a drone network map file.

    Reads a .txt map file, cleans it (comments, empty lines, newlines),
    and validates every line according to the subject specification.
    Stores parsed zones and connections for later use by the simulator.
    """

    def __init__(self, map_path: str) -> None:
        """Initializes the parser with a map file path.

        Args:
            map_path: Path to the .txt map file.
        """
        self.map_path = map_path
        self.nb_drones = 0
        self.start_count = 0
        self.end_count = 0
        self.zones: dict[str, Zones] = {}
        self.connections: dict[tuple[str, str], Connections] = {}

    def _read_map(self) -> list[tuple[int, str]]:
        """Reads the raw map file lines with their original line numbers.

        Returns:
            List of (line_number, raw_line) tuples.
        """
        with open(self.map_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        result = []
        for line_n, line in enumerate(data, start=1):
            result.append((line_n, line))
        return result

    def _clean_comments(self, data: list[tuple[int, str]]
                        ) -> list[tuple[int, str]]:
        """Removes comment lines (starting with '#').

        Args:
            data: List of (line_number, line) tuples.

        Returns:
            Filtered list without comment lines.
        """
        no_comments = []
        for line_n, line in data:
            if line.startswith('#'):
                continue
            no_comments.append((line_n, line))
        return no_comments

    def _clean_next_line(self, data: list[tuple[int, str]]
                         ) -> list[tuple[int, str]]:
        """Strips trailing newline characters from each line.

        Args:
            data: List of (line_number, line) tuples.

        Returns:
            List with newline characters removed.
        """
        no_next_line = []
        for line_n, line in data:
            line_cleaned = line.rstrip("\n")
            no_next_line.append((line_n, line_cleaned))
        return no_next_line

    def _clean_empty_lines(self, data: list[tuple[int, str]]
                           ) -> list[tuple[int, str]]:
        """Removes empty lines from the data.

        Args:
            data: List of (line_number, line) tuples.

        Returns:
            Filtered list without empty lines.
        """
        no_empty_lines = []
        for line_n, line in data:
            if line == "":
                continue
            no_empty_lines.append((line_n, line))
        return no_empty_lines

    def cleaned_map(self) -> list[tuple[int, str]]:
        """Reads the map file and applies all cleaning steps.

        Maintains the original line numbers for accurate error reporting.

        Returns:
            Cleaned list of (line_number, line) tuples.
        """
        data = self._read_map()
        data_no_comment = self._clean_comments(data)
        data_no_next_line = self._clean_next_line(data_no_comment)
        data_cleaned = self._clean_empty_lines(data_no_next_line)
        return data_cleaned

    def checking_data(self, data: list[tuple[int, str]]) -> None:
        """Validates every line of the cleaned map data.

        Dispatches lines to the appropriate parsing and validation
        methods based on their prefix (nb_drones, start_hub, hub,
        end_hub, connection).

        Args:
            data: Cleaned list of (line_number, line) tuples.

        Raises:
            Parser_Error: If any line is invalid or the map structure
                (exactly one start and one end) is violated.
        """
        self._validate_nb_drones(data[0])

        for line_n, line_text in data[1:]:
            if line_text.startswith("start_hub:"):
                tup_hub_config = self._parse_config_hubs(line_n, line_text,
                                                         "start_hub:")
                self._validate_hub("start", line_n, tup_hub_config)

            elif line_text.startswith("hub:"):
                tup_hub_config = self._parse_config_hubs(line_n, line_text,
                                                         "hub:")
                self._validate_hub("hub", line_n, tup_hub_config)

            elif line_text.startswith("end_hub:"):
                tup_hub_config = self._parse_config_hubs(line_n, line_text,
                                                         "end_hub:")
                self._validate_hub("end", line_n, tup_hub_config)

            elif line_text.startswith("connection:"):
                tup_conn_config = self._parse_config_connections(line_n,
                                                                 line_text,
                                                                 "connection:")
                self._validate_connection(line_n, tup_conn_config)
            else:
                raise Parser_Error(line_n, "invalid specification detected"
                                   f" in '{line_text}'")

        if self.start_count != 1 or self.end_count != 1:
            raise Parser_Error(0, "Map must contain exactly one "
                               "start_hub and one end_hub")

    def _parse_config_hubs(self, data_n: int, data_content: str, prefix: str
                           ) -> tuple[str, str, str, str]:
        """Splits a hub line into its raw components.

        Extracts name, x, y, and optional metadata string from a line
        starting with start_hub:, hub:, or end_hub:.

        Args:
            data_n: Line number for error reporting.
            data_content: The full raw line content.
            prefix: The hub prefix ("start_hub:", "hub:", or "end_hub:").

        Returns:
            Tuple of (name, x, y, metadata), where x and y are strings
            and metadata is the raw bracket content (or "").

        Raises:
            Parser_Error: If the line structure is invalid.
        """
        body = data_content.replace(prefix, "", 1).strip()
        i = 0
        if "[" not in body:
            list_simple_data = body.split()
            if len(list_simple_data) == 3:
                name = list_simple_data[0]
                x = list_simple_data[1]
                y = list_simple_data[2]
                metadata = ""
                tup_simple_data = (name, x, y, metadata)
                return tup_simple_data
            else:
                raise Parser_Error(data_n, "Invalid structure of the hub."
                                   " It should be: <name> <x> <y>,"
                                   f"\n but found: '{data_content}'")

        else:
            start_meta = 0
            while i < len(body):
                if body[i] == "[":
                    start_meta = i
                i += 1
            metadata = body[start_meta:]
            main_part = body[:start_meta - 1].strip()
            list_complex_data = main_part.split()
            if not metadata.endswith("]") or len(list_complex_data) != 3:
                raise Parser_Error(data_n, "Invalid structure of the hub."
                                   " It should be: <name> <x> <y> [metadata],"
                                   f"\n but found: '{data_content}'")
            else:
                name = list_complex_data[0]
                x = list_complex_data[1]
                y = list_complex_data[2]
                tup_complex_data = (name, x, y, metadata)
                return tup_complex_data

    def _parse_config_connections(self, data_n: int,
                                  data_content: str,
                                  prefix: str
                                  ) -> tuple[str, str, str]:
        """Splits a connection line into its raw components.

        Extracts zone1, zone2, and optional metadata from a line
        starting with connection:.

        Args:
            data_n: Line number for error reporting.
            data_content: The full raw line content.
            prefix: The connection prefix ("connection:").

        Returns:
            Tuple of (name1, name2, metadata).

        Raises:
            Parser_Error: If the line structure is invalid.
        """
        body = data_content.replace(prefix, "", 1).strip()
        if "[" not in body:
            names = body.split("-")
            metadata = ""
        else:
            i = 0
            start_meta = 0
            while i < len(body):
                if body[i] == "[":
                    start_meta = i
                i += 1
            metadata = body[start_meta:]
            main_part = body[:start_meta - 1].strip()
            names = main_part.split("-")
            if not metadata.endswith("]"):
                raise Parser_Error(data_n, "Invalid structure of connection."
                                   " It should be: <name1>-<name2> [metadata],"
                                   f"\n but found: {data_content}")
        if len(names) != 2:
            raise Parser_Error(data_n, "The connection needs two zones")
        name1 = names[0]
        name2 = names[1]
        if not name1 or not name2:
            raise Parser_Error(data_n, "The connection needs two zones")
        tup_data = (name1, name2, metadata)
        return tup_data

    def _validate_nb_drones(self, data: tuple[int, str]) -> None:
        """Validates the nb_drones line.

        Ensures the first line specifies a positive integer for
        the number of drones.

        Args:
            data: Tuple of (line_number, line_text).

        Raises:
            Parser_Error: If nb_drones is missing, not an integer,
                or not positive.
        """
        data_0_n, data_0_line = data

        if not data_0_line.startswith("nb_drones:"):
            raise Parser_Error(data_0_n, "missing the "
                               "specification of 'nb_drones: <int>'")

        number_nb = data_0_line.replace("nb_drones:", "").strip()

        try:
            self.nb_drones = int(number_nb)
        except ValueError:
            raise Parser_Error(data_0_n, "Invalid amount passed to 'nb_drones'"
                               f", passed argument: '{number_nb}'")

        if self.nb_drones <= 0:
            raise Parser_Error(data_0_n, "Invalid amount passed to 'nb_drones'"
                               ", the specified quantity should be a value"
                               " greater than 0. "
                               f"Passed argument: '{number_nb}'")

    def _validate_hub(self, role: str, data_n: int,
                      data_tuple: tuple[str, str, str, str]) -> None:
        """Validates and stores a zone parsed from a hub line.

        Checks for duplicate names, invalid characters in names,
        invalid coordinates, and enforces exactly one start and
        one end zone.

        Args:
            role: Zone role — "start", "hub", or "end".
            data_n: Line number for error reporting.
            data_tuple: Tuple of (name, x_str, y_str, metadata).

        Raises:
            Parser_Error: If any validation constraint is violated.
        """
        name, x, y, metadata = data_tuple
        try:
            x = int(x)
            y = int(y)
        except ValueError:
            raise Parser_Error(data_n, "Invalid coordinates of the hub, "
                               "the given values to x or y are not an int")

        if name in self.zones:
            raise Parser_Error(data_n, f"The zones created must be unique."
                               f" Found duplicates for {name}")

        if "-" in name:
            raise Parser_Error(data_n, "The name cannot use '-'. "
                               f"The given name has been: '{name}'")

        if " " in name:
            raise Parser_Error(data_n, "The name cannot contain spaces. "
                               f"The given name has been: '{name}'")

        if role == "start":
            self.start_count += 1

        if role == "end":
            self.end_count += 1

        if self.end_count > 1 or self.start_count > 1:
            raise Parser_Error(data_n, "There must be only one zone for the "
                               "start and end. Found duplicates.")

        self.zones[name] = Zones(name, x, y, metadata, role, data_n)

    def _validate_connection(self, data_n: int,
                             data_tuple: tuple[str, str, str]) -> None:
        """Validates and stores a parsed connection.

        Checks that both referenced zones exist, they are different,
        and the connection is not a duplicate (a-b and b-a treated
        as the same).

        Args:
            data_n: Line number for error reporting.
            data_tuple: Tuple of (name1, name2, metadata).

        Raises:
            Parser_Error: If any validation constraint is violated.
        """
        name1, name2, metadata = data_tuple
        if name1 not in self.zones or name2 not in self.zones:
            raise Parser_Error(data_n, "The zone specified in the connection"
                               " doesn't exist")
        if name1 == name2:
            raise Parser_Error(data_n, "The zones in the connection "
                               "are the same")
        key: tuple[str, str]
        if name1 <= name2:
            key = (name1, name2)
        else:
            key = (name2, name1)
        if key in self.connections:
            raise Parser_Error(data_n, "The connection already exists")
        self.connections[key] = Connections(name1, name2, metadata, data_n)
