class Parser_Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MapParser():
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path

    def read_map(self) -> list[tuple[int, str]]:
        with open(self.map_path, "r", encoding="utf-8") as file:
            data = file.readlines()

        result = []
        for line_n, line in enumerate(data, start=1):
            result.append((line_n, line))
        return result

    def clean_comments(self, data: list[tuple[int, str]]
                       ) -> list[tuple[int, str]]:
        no_comments = []
        for line_n, line in data:
            if line.startswith('#'):
                continue
            no_comments.append((line_n, line))
        return no_comments

    def clean_next_line(self, data: list[tuple[int, str]]
                        ) -> list[tuple[int, str]]:
        no_next_line = []
        for line_n, line in data:
            line_cleaned = line.rstrip("\n")
            no_next_line.append((line_n, line_cleaned))
        return no_next_line

    def clean_empty_lines(self, data: list[tuple[int, str]]
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
        data = self.read_map()
        data_no_comment = self.clean_comments(data)
        data_no_next_line = self.clean_next_line(data_no_comment)
        data_cleaned = self.clean_empty_lines(data_no_next_line)
        return data_cleaned

    def checking_data(self, data: list[tuple[int, str]]):
        # Check: nb_drones
        data_0_n, data_0_line = data[0]
        if not data_0_line.startswith("nb_drones"):
            print(f"Error at line: {data_0_n}, missing the specification"
                  " of 'nb_drones: <int>'")

        # Check: start_hub
        data_1_n, data_1_line = data[1]
        if not data_1_line.startswith("start_hub"):
            print(f"Error at line: {data_1_n}, missing the specification"
                  " of 'start_hub': <hub configuration>'")

        # Check: hub
        counter_hubs = 0
        for data_n, data_line in data[2:]:
            counter_hubs += 1
            if not data_line.startswith("hub:") and counter_hubs > 0:
                print(f"Error in line: {data_n}, missing the specification of 'hub': <hub configuration>")
                break

        # Check: end_hub
        data_2_n, data_2_line = data[2]
        if not data_2_line.startswith("end_hub"):
            print(f"Error at line: {data_2_n}, missing the specification"
                  " of 'end_hub': <hub configuration>'")

# def read_map(map: MapParser):
