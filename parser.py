from errors import Parser_Error
from zones import Zones
from connections import Connections


class MapParser():
    """Reads, cleans, validates, and stores a drone network map.

    The map file describes zones and connections. This class
    processes it into dictionaries of Zone and Connection objects
    ready for the simulator.

    Args:
        map_path: Path to a .txt map file.
    """

    def __init__(self, map_path: str) -> None:
        """Initializes the parser.

        Call cleaned_map() then checking_data() to parse.

        Args:
            map_path: Path to a .txt map file.
        """
        self.map_path = map_path
        self.nb_drones = 0
        self.start_count = 0
        self.end_count = 0
        self.zones: dict[str, Zones] = {}
        self.connections: dict[tuple[str, str], Connections] = {}

    def _read_map(self) -> list[tuple[int, str]]:
        """Reads the file and returns each line with its line number.

        Returns:
            List of (line_number, line_text). Line numbers start at 1.
        """
        with open(self.map_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        result = []
        for line_n, line in enumerate(data, start=1):
            result.append((line_n, line))
        return result

    def _clean_comments(self, data: list[tuple[int, str]]
                        ) -> list[tuple[int, str]]:
        """Removes lines starting with '#'.

        Args:
            data: List of (line_number, line) tuples.

        Returns:
            List without comment lines.
        """
        no_comments = []
        for line_n, line in data:
            if line.startswith('#'):
                continue
            no_comments.append((line_n, line))
        return no_comments

    def _clean_next_line(self, data: list[tuple[int, str]]
                         ) -> list[tuple[int, str]]:
        """Strips the trailing newline from every line.

        Args:
            data: List of (line_number, line) tuples.

        Returns:
            List with newlines removed from each line text.
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
            List without empty lines.
        """
        no_empty_lines = []
        for line_n, line in data:
            if line == "":
                continue
            no_empty_lines.append((line_n, line))
        return no_empty_lines

    def cleaned_map(self) -> list[tuple[int, str]]:
        """Reads and cleans the map file.

        Removes comments, newlines, and empty lines while preserving
        original line numbers for error messages.

        Returns:
            Cleaned list of (line_number, line_text).
        """
        data = self._read_map()
        data_no_comment = self._clean_comments(data)
        data_no_next_line = self._clean_next_line(data_no_comment)
        data_cleaned = self._clean_empty_lines(data_no_next_line)
        return data_cleaned

    def checking_data(self, data: list[tuple[int, str]]) -> None:
        """Validates all lines and builds internal data structures.

        Processes nb_drones, start_hub, hub, end_hub, and connection
        lines. Ensures exactly one start and one end hub exist.

        Args:
            data: Cleaned list of (line_number, line_text).

        Raises:
            Parser_Error: If any line is invalid or the map structure
                is violated.
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
        """Splits a hub line into name, x, y, and optional metadata.

        Args:
            data_n: Line number for error messages.
            data_content: The full raw line.
            prefix: "start_hub:", "hub:", or "end_hub:".

        Returns:
            Tuple of (name, x_str, y_str, metadata). metadata is ""
            if no brackets were found.

        Raises:
            Parser_Error: If the line structure is wrong.
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
        """Splits a connection line into zone1, zone2, and metadata.

        Args:
            data_n: Line number for error messages.
            data_content: The full raw line.
            prefix: "connection:".

        Returns:
            Tuple of (zone1, zone2, metadata).

        Raises:
            Parser_Error: If the structure is wrong.
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
        """Checks the first line is 'nb_drones: <positive integer>'.

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
        """Validates a zone line and stores it as a Zones object.

        Args:
            role: "start", "hub", or "end".
            data_n: Line number for error messages.
            data_tuple: (name, x_str, y_str, metadata) from
                _parse_config_hubs.

        Raises:
            Parser_Error: If any validation fails.
        """
        name, x_str, y_str, metadata = data_tuple
        try:
            x = int(x_str)
            y = int(y_str)
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
        """Validates a connection line and stores a Connections object.

        Args:
            data_n: Line number for error messages.
            data_tuple: (zone1, zone2, metadata) from
                _parse_config_connections.

        Raises:
            Parser_Error: If any validation fails.
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
