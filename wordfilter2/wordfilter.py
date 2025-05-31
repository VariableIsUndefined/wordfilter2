import os
import re
from typing import Callable


class WordFilter:
    ALLOWED_EXTENSIONS = {'txt'}

    def __init__(self,
                 ignore_case: bool=True,
                 partial_match: bool=True,
                 replace_with: str="*",
                 replace_with_func: Callable[[str], str]=None) -> None:
        """
        Initialize a new WordFilter instance.

        Args:
            ignore_case (bool): Whether to ignore case when matching words.
            partial_match (bool): Whether to match partial words.
            replace_with (str): Character or string to replace filtered words with.
            replace_with_func (Callable[[str], str], optional): Custom function to generate replacement for matched words.
        """
        if replace_with_func is not None and not callable(replace_with_func):
            raise TypeError('`replace_with_func` must be a callable or None')

        self.words: set[str] = set()
        self.ignore_case: bool = ignore_case
        self.partial_match: bool = partial_match
        self.replace_with: str = replace_with
        self.replace_with_func = replace_with_func

    def normalize(self, word: str) -> str:
        """
        Normalize a word based on the case sensitivity setting.

        Args:
            word (str): The word to normalize.

        Returns:
            str: Normalized word.
        """
        return word.lower() if self.ignore_case else word

    def add_word(self, word: str) -> None:
        """
        Add a single word to the filter list.

        Args:
            word (str): Word to be added.

        Raises:
            TypeError: If word is not a string.
        """
        if not isinstance(word, str):
            raise TypeError('Word must be a string')

        self.words.add(self.normalize(word.strip()))

    def add_words(self, words: set[str] | list[str] | tuple[str]) -> None:
        """
        Add multiple words to the filter list.

        Args:
            words (set, list, or tuple of str): Words to be added.

        Raises:
            ValueError: If words is empty.
            TypeError: If words is not a collection of strings.
        """
        if not words:
            raise ValueError('No words provided')

        if not isinstance(words, (set, list, tuple)):
            raise TypeError('Words must be a set, list or tuple')

        for word in words:
            self.add_word(word)

    def remove_word(self, word: str) -> None:
        """
        Remove a word from the filter list.

        Args:
            word (str): Word to be removed.

        Raises:
            TypeError: If word is not a string.
        """
        if not isinstance(word, str):
            raise TypeError('Word must be a string')

        self.words.discard(word)

    def filter(self, text: str) -> str:
        """
        Replace filtered words in the given text.

        Args:
            text (str): The input text to filter.

        Returns:
            str: The filtered text with matched words replaced.

        Raises:
            ValueError: If text is empty.
            TypeError: If text is not a string.
        """
        if not text:
            raise ValueError('No text provided')

        if not isinstance(text, str):
            raise TypeError('Text must be a string')

        def replace(match: re.Match) -> str:
            word = match.group()
            if self.replace_with_func is not None:
                return self.replace_with_func(word)

            replacement = self.replace_with * len(word) if len(self.replace_with) == 1 else self.replace_with
            return replacement.strip()

        if not self.words:
            return text

        normalized_banned = set(map(self.normalize, self.words))
        words_pattern = '|'.join(re.escape(word) for word in normalized_banned)

        if self.partial_match:
            pattern = fr'\b\w*({words_pattern})\w*\b'
        else:
            pattern = fr'\b({words_pattern})\b'

        flags = re.IGNORECASE if self.ignore_case else 0
        regex = re.compile(pattern, flags)

        return regex.sub(replace, text)

    def contains_profanity(self, text: str) -> bool:
        """
        Check if the given text contains any filtered words.

        Args:
            text (str): The input text to check.

        Returns:
            bool: True if text contains any banned word, False otherwise.

        Raises:
            ValueError: If text is empty.
            TypeError: If text is not a string.
        """
        if not text:
            raise ValueError('No text provided')

        if not isinstance(text, str):
            raise TypeError('Text must be a string')

        normalized_banned = set(map(self.normalize, self.words))
        words_pattern = '|'.join(re.escape(word) for word in normalized_banned)
        pattern = fr'\b(?:{words_pattern})\b' if not self.partial_match else fr'(?:{words_pattern})'
        regex = re.compile(pattern, re.IGNORECASE if self.ignore_case else 0)

        return bool(regex.search(text))

    def load_from_file(self, path: str) -> None:
        """
        Load words from a file and add them to the filter list.

        Args:
            path (str): Path to the text file containing banned words.

        Raises:
            TypeError: If path is not a string.
            FileNotFoundError: If the file does not exist.
            ValueError: If the file has an unsupported extension.
        """
        if not isinstance(path, str):
            raise TypeError('Path must be a string')

        if not os.path.isfile(path):
            raise FileNotFoundError(f'File {path} not found')

        if path.split('.')[-1] not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f'File extension {path.split(".")[-1]!r} not allowed')

        with open(path, 'r', encoding='utf-8') as file:
            for line in file:
                self.words.add(line.strip())

    def save_to_file(self, path: str) -> None:
        """
        Save the current list of filtered words to a file.

        Args:
            path (str): Path to the output file.

        Raises:
            TypeError: If path is not a string.
        """
        if not isinstance(path, str):
            raise TypeError('Path must be a string')

        with open(path, 'w', encoding='utf-8') as file:
            for word in self.words:
                file.write(word + '\n')