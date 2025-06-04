"""
Utils file which provides different types of censoring for wordfilter2
"""

from typing import Callable


def mask_full(char: str = "*") -> Callable[[str], str]:
    """
    Replaces a word with a chars

    Args:
        char (str, optional): Character or string to replace filtered word.

    Returns:
        Callable[[str], str]: Censor-function.
    """
    def replace(word: str) -> str:
        return char * len(word)

    return replace


def mask_partial(char: str = "*") -> Callable[[str], str]:
    """
    Leaves the first and last characters, replaces the rest with char

    Args:
        char (str, optional): Character or string to replace filtered word.

    Returns:
        Callable[[str], str]: Censor-function.
    """
    def replace(word: str) -> str:
        if len(word) <= 2:
            return char * len(word)
        return word[0] + char * (len(word) - 2) + word[-1]

    return replace


def mask_first_last(char: str = "*") -> Callable[[str], str]:
    """
    Leaves only the first character

    Args:
        char (str, optional): Character or string to replace filtered word.

    Returns:
        Callable[[str], str]: Censor-function.
    """

    def replace(word: str) -> str:
        return word[0] + char * (len(word) - 1)

    return replace


def mask_censor(char: str = "*") -> Callable[[str], str]:
    """
    Replaces all letters except the first and last with a character, but not less than 2 characters

    Args:
        char (str, optional): Character or string to replace filtered word.

    Returns:
        Callable[[str], str]: Censor-function.
    """
    def replace(word: str) -> str:
        if len(word) < 2:
            return char * len(word)
        return word[0] + char * (len(word) - 2) + word[-1]
    return replace


def mask_custom(template: str = "*") -> Callable[[str], str]:
    """
    Custom template replacement

    Args:
        template (str, optional): Character or string to replace filtered word.

    Returns:
        Callable[[str], str]: Censor-function.
    """
    def replace(word: str) -> str:
        return template
    return replace