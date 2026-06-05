class Parser_Error(Exception):
    def __init__(self, line_n: int, msg: str) -> None:
        super().__init__(f"Error at line {line_n}: {msg}")


class MapParser():
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
        self.nb_drones = 0

    def _read_map(self) -> list[tuple[int, str]]:
        with open(self.map_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        result = []
        for line_n, line in enumerate(data, start=1):
            result.append((line_n, line))
        return result

    def _clean_comments(self, data: list[tuple[int, str]]
                        ) -> list[tuple[int, str]]:
        no_comments = []
        for line_n, line in data:
            if line.startswith('#'):
                continue
            no_comments.append((line_n, line))
        return no_comments

    def _clean_next_line(self, data: list[tuple[int, str]]
                         ) -> list[tuple[int, str]]:
        no_next_line = []
        for line_n, line in data:
            line_cleaned = line.rstrip("\n")
            no_next_line.append((line_n, line_cleaned))
        return no_next_line

    def _clean_empty_lines(self, data: list[tuple[int, str]]
                           ) -> list[tuple[int, str]]:
        no_empty_lines = []
        for line_n, line in data:
            if line == "":
                continue
            no_empty_lines.append((line_n, line))
        return no_empty_lines

    def cleaned_map(self) -> list[tuple[int, str]]:
        """
        Gets the map path argument, obtains the raw data and cleans it.
        Maintaining the original line indexes in case a parsing error
        needs to be reported.
        """
        data = self._read_map()
        data_no_comment = self._clean_comments(data)
        data_no_next_line = self._clean_next_line(data_no_comment)
        data_cleaned = self._clean_empty_lines(data_no_next_line)
        return data_cleaned

    def checking_data(self, data: list[tuple[int, str]]) -> None:
        # Check: nb_drones always at first line
        self._validate_nb_drones(data[0])

        # Dispatcher for the rest of categories
        for line_n, line_text in data[1:]:
            if line_text.startswith("start_hub:"):
                self._validate_start_hub(line_n, line_text)
            elif line_text.startswith("hub:"):
                self._validate_hub(line_n, line_text)
            elif line_text.startswith("end_hub:"):
                self._validate_end_hub(line_n, line_text)
            elif line_text.startswith("connection:"):
                self._validate_connection(line_n, line_text)
            else:
                raise Parser_Error(line_n, "invalid specification detected"
                                   f" in '{line_text}'")

    def _validate_nb_drones(self, data: tuple[int, str]) -> None:

        data_0_n, data_0_line = data

        if not data_0_line.startswith("nb_drones:"):
            raise Parser_Error(data_0_n, "missing the "
                               "specification of 'nb_drones: <int>'")

        # Recollection of the nb_drones specified
        index_number = data_0_line.index(":")
        number_nb = ""
        for char in data_0_line:
            if data_0_line.index(char) <= (index_number + 1):
                continue
            number_nb = number_nb + char

        # Conversion to int
        try:
            self.nb_drones = int(number_nb)
        except ValueError:
            raise Parser_Error(data_0_n, "Invalid amount passed to 'nb_drones'"
                               f", passed argument: '{number_nb}'")

        # Checking if it fits the valid range
        if self.nb_drones <= 0:
            raise Parser_Error(data_0_n, "Invalid amount passed to 'nb_drones'"
                               ", the specified quantity should be a value"
                               " greater than 0. "
                               f"Passed argument: '{number_nb}'")
    
    def _validate_start_hub(self, data_n, data_content) -> None:
        list_config = data_content.split()
        if len(list_config) == 5 or len(list_config) == 4:
            name = list_config[1]
            x = list_config[2]
            y = list_config[3]
            if len(list_config) == 5:
                meta = list_config[4]
            try:
                x = int(x)
                y = int(y)
            except ValueError:
                raise Parser_Error(data_n, f"Invalid coordinates of the hub, the given value is not an int:\n   '{data_content}'")
        else:
            raise Parser_Error(data_n, "Invalid configuration of the hub. It should follow the structure of: \n"
                               "    hub: <name> <x> <y> [metadata]")
        # Primero sale hub: y luego lo demás, lo de antes de los dos puntos, obviar.
        