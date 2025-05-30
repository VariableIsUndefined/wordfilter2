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

        if replace_with_func is not None and not callable(replace_with_func):
            raise TypeError('`replace_with_func` must be a callable or None')

        self.words: set[str] = set()
        self.ignore_case: bool = ignore_case
        self.partial_match: bool = partial_match
        self.replace_with: str = replace_with
        self.replace_with_func = replace_with_func

    def normalize(self, word: str) -> str:
        return word.lower() if self.ignore_case else word

    def add_word(self, word: str) -> None:
        if not isinstance(word, str):
            raise TypeError('Word must be a string')

        self.words.add(self.normalize(word.strip()))

    def add_words(self, words: set[str] | list[str] | tuple[str]) -> None:
        if not words:
            raise ValueError('No words provided')

        if not isinstance(words, (set, list, tuple)):
            raise TypeError('Words must be a set, list or tuple')

        for word in words:
            self.add_word(word)

    def remove_word(self, word: str) -> None:
        if not isinstance(word, str):
            raise TypeError('Word must be a string')

        self.words.discard(word)

    def filter(self, text: str) -> str:
        if not text:
            raise ValueError('No text provided')

        if not isinstance(text, str):
            raise TypeError('Text must be a string')

        def replace(match: re.Match) -> str:
            word = match.group()
            if self.replace_with_func is not None:
                return self.replace_with_func(word)

            replacement = self.replace_with * len(word) if len(self.replace_with) == 1 else self.replace_with
            return replacement

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
        if not isinstance(path, str):
            raise TypeError('Path must be a string')

        with open(path, 'w', encoding='utf-8') as file:
            for word in self.words:
                file.write(word + '\n')