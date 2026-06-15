"""ANSI color codes for terminal output.

Each zone can declare a color in its metadata (e.g. color=green).
This module maps those names to ANSI escape sequences.
"""

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
    code = COLOR_MAP.get(color_name.lower())
    if code is None:
        return text
    return f"{code}{text}{RESET}"
