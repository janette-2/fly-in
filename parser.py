class Parser_Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MapParser():
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path

    def read_map(self) -> list[str]:
        with open(self.map_path, "r", encoding="utf-8") as file:
            data = file.readlines()
        return data

    def clean_comments(self, data: list[str]) -> list[str]:
        for line in data:
            if line.startswith('#'):
                data.remove(line)
        return data

    def clean_next_line(self, data: list[str]) -> list[str]:
        for i, line in enumerate(data):
            data[i] = line.rstrip("\n")
        return data

    def clean_empty_lines(self, data: list[str]) -> list[str]:
        for line in data:
            if line == "":
                data.remove(line)
        return data

# def read_map(map: MapParser):
