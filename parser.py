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

# def read_map(map: MapParser):
