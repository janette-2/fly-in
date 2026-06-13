class Parser_Error(Exception):
    """Exception raised when a map file contains invalid data.

    This is the only custom exception in the project.
    It is raised whenever the parser encounters something that
    does not match the subject specification (wrong syntax,
    missing data, invalid zone types, duplicate names, etc.).

    Attributes:
        line_n: Line number in the map file where the error was found.
        msg: Human-readable description of what went wrong.
    """

    def __init__(self, line_n: int, msg: str) -> None:
        """Stores the line number and error message, then formats them.

        The parent Exception class receives a string like:
        "Error at line 12: Invalid zone type: 'super_fast'"

        Args:
            line_n: Line number of the error (1-based).
            msg: Description of the problem.
        """
        super().__init__(f"Error at line {line_n}: {msg}")
