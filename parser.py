class Parser_Error(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class MapParser():
    def __init__(self, map_path: str) -> None:
        self.map_path = map_path
   
