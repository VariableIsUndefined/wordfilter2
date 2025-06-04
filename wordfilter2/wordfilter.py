import os
import re
import json
from typing import Callable, Optional, Set

import requests


class WordFilter:
    ALLOWED_EXTENSIONS = {
        'txt',
        'json'
    }

    def __init__(self,
                 ignore_case: bool=True,
                 partial_match: bool=True,
                 replace_with: str="*",
                 replace_with_func: Callable[[str], str]=None,
                 normalize_spaces: bool=True) -> None:
        """
        Initialize a new WordFilter instance.

        Args:
            ignore_case (bool): Whether to ignore case when matching words.
            partial_match (bool): Whether to match partial words.
            replace_with (str): Character or string to replace filtered words with.
            replace_with_func (Callable[[str], str], optional): Custom function to generate replacement for matched words.
            normalize_spaces (bool): Whether to keep one space between each word.
        """
        if replace_with_func is not None and not callable(replace_with_func):
            raise TypeError('`replace_with_func` must be a callable or None')

        self.words: Set[str] = set()
        self.ignore_case: bool = ignore_case
        self.partial_match: bool = partial_match
        self.replace_with: str = replace_with
        self.replace_with_func: Callable[[str], str] = replace_with_func
        self.normalize_spaces: bool = normalize_spaces

        self._regex_cache: Optional[re.Pattern] = None
        self._last_words_hash: int = 0

    def _invalidate_cache(self) -> None:
        """Clearing cache upon updating words."""
        self._regex_cache = None
        self._last_words_hash = 0

    def _get_cached_regex(self) -> re.Pattern:
        """Creates or returns cache regex."""
        current_words_hash = hash(frozenset(self.words))
        if self._regex_cache is not None and self._last_words_hash == current_words_hash:
            return self._regex_cache

        if not self.words:
            self._regex_cache = re.compile(r"(?!)")
            self._last_words_hash = current_words_hash
            return self._regex_cache

        normalized_banned = map(self.normalize, self.words)
        pattern_str = "|".join(re.escape(word) for word in normalized_banned)
        if self.partial_match:
            pattern = f"({pattern_str})"
        else:
            pattern = fr"\b({pattern_str})\b"

        flags = re.IGNORECASE if self.ignore_case else 0
        self._regex_cache = re.compile(pattern, flags | re.UNICODE)
        self._last_words_hash = current_words_hash
        return self._regex_cache

    def normalize(self, word: str) -> str:
        """
        Normalize a word based on the case sensitivity setting.

        Args:
            word (str): The word to normalize.

        Returns:
            str: Normalized word.
        """
        return word.lower() if self.ignore_case else word

    def add_word(self, word: str, ignore_duplicates: bool=False) -> None:
        """
        Add a single word to the filter list.

        Args:
            word (str): Word to be added.
            ignore_duplicates (bool, optional): If duplicated should be ignored.

        Raises:
            TypeError: If word is not a string.
            ValueError: If word is duplicated.
        """
        if not isinstance(word, str):
            raise TypeError('Word must be a string')

        normalized = self.normalize(word.strip())
        if not ignore_duplicates and normalized in self.words:
            raise ValueError(f"Word '{word}' already exists")

        self.words.add(normalized)
        self._invalidate_cache()

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

        if not isinstance(words, (set, list, tuple)) or not all(isinstance(word, str) for word in words):
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

        self.words.discard(self.normalize(word.strip()))
        self._invalidate_cache()

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

        if not self.words:
            return text

        regex = self._get_cached_regex()

        def replace(match: re.Match) -> str:
            word = match.group()
            if self.replace_with_func:
                return self.replace_with_func(word)
            return self.replace_with * len(word) if len(self.replace_with) == 1 else self.replace_with

        result = regex.sub(replace, text)
        return self.normalize_spaces and re.sub(" +", " ", result).strip() or result.strip()

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

        if not self.words:
            return False

        regex = self._get_cached_regex()
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
            ValueError: If the JSON list has non-strings elements.
        """
        if not isinstance(path, str):
            raise TypeError("Path must be a string")
        if not os.path.isfile(path):
            raise FileNotFoundError(f"File {path} not found")

        ext = os.path.splitext(path)[1][1:].lower()
        if ext not in self.ALLOWED_EXTENSIONS:
            raise ValueError(f"File extension '{ext}' not allowed")

        with open(path, encoding="utf-8") as f:
            if ext == "json":
                data = json.load(f)
                if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
                    raise ValueError("File must contain a list of strings")
                self.add_words(data)
            else:
                for line in f:
                    self.add_word(line.strip())

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

        with open(path, "w", encoding="utf-8") as f:
            for word in sorted(self.words):
                f.write(word + "\n")

    def load_from_url(self, url: str) -> None:
        """
        Load words from a remote file (txt or json).

        Args:
            url (str): URL to the remote file.

        Raises:
            TypeError: If url is not a string.
            ValueError: If JSON does not contain any strings.
            ValueError: if Content-Type is not supported.
        """

        if not isinstance(url, str):
            raise TypeError("URL must be a string")
        response = requests.get(url)
        response.raise_for_status()
        content_type = response.headers.get("Content-Type", "")

        if "json" in content_type:
            data = response.json()
            if not isinstance(data, list) or not all(isinstance(item, str) for item in data):
                raise ValueError("Remote file must contain a list of strings")
            self.add_words(data)
        elif "text/plain" in content_type:
            for line in response.text.splitlines():
                self.add_word(line.strip())
        else:
            raise ValueError(f"Unsupported Content-Type: {content_type}")

    def clear(self) -> None:
        """Remove all filtered words"""
        self.words.clear()
        self._invalidate_cache()

    def find_matches(self, text: str) -> list[str]:
        """Find censored (matched) words"""
        regex = self._get_cached_regex()
        return regex.findall(text)

    def remove_words_containing(self, substring: str) -> None:
        """
        Remove all words containing the given substring.

        Args:
            substring (str): Substring to match for removal.
        """
        normalized_sub = self.normalize(substring)
        self.words = {word for word in self.words if normalized_sub not in word}
        self._invalidate_cache()