class Parser_Error(Exception):
    """Raised when a map file contains invalid data.

    Args:
        line_n: Line number where the error was found.
        msg: Human-readable description of the problem.
    """

    def __init__(self, line_n: int, msg: str) -> None:
        """Initializes the exception with a formatted error message.

        Args:
            line_n: Line number of the error (1-based).
            msg: Description of the problem.
        """
        super().__init__(f"Error at line {line_n}: {msg}")
