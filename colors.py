"""ANSI colour codes for terminal output."""

COLOR_MAP = {
    "green": "\033[32m",
    "red": "\033[31m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "yellow": "\033[33m",
    "pink": "\033[35m",
    "purple": "\033[35m",
    "orange": "\033[38;5;208m",
    "grey": "\033[38;5;244m",
}

RESET = "\033[0m"


def colorize(text: str, color_name: str) -> str:
    """Wraps text in ANSI colour codes for terminal display.

    Args:
        text: The string to colour.
        color_name: A colour name ("red", "green", "blue", etc.),
            case-insensitive.

    Returns:
        The coloured string with ANSI codes, or the original text
        if the colour is unknown.
    """
    code = COLOR_MAP.get(color_name.lower())
    if code is None:
        return text
    return f"{code}{text}{RESET}"
