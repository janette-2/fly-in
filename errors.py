class Parser_Error(Exception):
    """Exception raised for parsing errors in map files.

    Attributes:
        line_n: Line number where the error occurred.
        msg: Description of the error.
    """

    def __init__(self, line_n: int, msg: str) -> None:
        """Initializes Parser_Error with a line number and message.

        Args:
            line_n: Line number of the error in the map file.
            msg: Human-readable error description.
        """
        super().__init__(f"Error at line {line_n}: {msg}")
