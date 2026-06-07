class Parser_Error(Exception):
    def __init__(self, line_n: int, msg: str) -> None:
        super().__init__(f"Error at line {line_n}: {msg}")


class MapParser():
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
        self.nb_drones = 0
        self.name_start = ""
        self.meta_start = ""
        self.x_start = 0
        self.y_start = 0
        self.name_end = ""
        self.meta_end = ""
        self.x_end = 0
        self.y_end = 0

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

    def _parse_config_hubs(self, data_n: int, data_content: str, prefix: str
                           ) -> tuple[str, str, str, str]:
        """
        Se le pasa el nº de línea, el contenido y el prefijo del dato
        (desde el dispatcher de chacking_data)

        Devuelve los datos separados adecuadamente:
            name : str
            x : str
            y : str
            meta: str
        """
        # Strip only erases the spaces at the start or end of a string
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
                                   f"\n but found: {data_content}")

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
                                   f"\n but found: {data_content}")
            else:
                name = list_complex_data[0]
                x = list_complex_data[1]
                y = list_complex_data[2]
                tup_complex_data = (name, x, y, metadata)
                return tup_complex_data

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

    def _validate_start_hub(self, data_n: int, data_content: str) -> None:
        list_config = data_content.split()
        if len(list_config) == 5 or len(list_config) == 4:
            self.name_start = list_config[1]
            x = list_config[2]
            y = list_config[3]
            if len(list_config) == 5:
                self.meta_start = list_config[4]
            try:
                self.x_start = int(x)
                self.y_start = int(y)
            except ValueError:
                raise Parser_Error(data_n, "Invalid coordinates of the hub, "
                                   "the given value is not an int:\n"
                                   f"   '{data_content}'")
        else:
            raise Parser_Error(data_n, "Invalid configuration of the hub."
                               " It should follow the structure of: \n"
                               "    hub: <name> <x> <y> [metadata]")

    def _validate_end_hub(self, data_n: int, data_content: str) -> None:
        list_config = data_content.split()
        if len(list_config) == 5 or len(list_config) == 4:
            self.name_end = list_config[1]
            x = list_config[2]
            y = list_config[3]
            if len(list_config) == 5:
                self.meta_end = list_config[4]
            try:
                self.x_end = int(x)
                self.y_end = int(y)
            except ValueError:
                raise Parser_Error(data_n, "Invalid coordinates of the hub, "
                                           "the given value is not an int:\n"
                                           f"   '{data_content}'")
        else:
            raise Parser_Error(data_n, "Invalid configuration of the hub."
                                       " It should follow the structure of: \n"
                                       "    hub: <name> <x> <y> [metadata]")
        # Primero sale hub: y luego lo demás, lo de
        # antes de los dos puntos, obviar.
