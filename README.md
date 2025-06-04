# WordFilter2

A powerful and customizable library for filtering profanity in Python.

[![PyPI version](https://img.shields.io/pypi/v/wordfilter2)](https://pypi.org/project/wordfilter2/) 

## Features

-----

- Case-insensitive filtering
- Full or partial matching
- Custom replacement functions
- Load from local file or URL
- Supports multiple formats (txt, json)

## Installation

-----

```bash
pip install wordfilter2
```

## Usage

-----

```python
from wordfilter2 import WordFilter

# Initialize the filter
wf = WordFilter(ignore_case=True, partial_match=False, replace_with="*")

# Add words to filter
wf.add_words(["badword", "offensive"])

# Filter text
filtered = wf.filter("This is a badword example.")
print(filtered)  # Output: This is a ******* example.

# Check if text contains profanity
contains = wf.contains_profanity("Something offensive here.")
print(contains)  # Output: True
```

## Custom Replacement

-----

```python
from wordfilter2 import WordFilter

def censor(word: str) -> str:
    return "[" + word.upper() + "]"

wf = WordFilter(replace_with_func=censor)
wf.add_word("spoiler")
print(wf.filter("This is a spoiler."))  # Output: This is a [SPOILER].
```

or

```python
from wordfilter2 import WordFilter

wf = WordFilter(replace_with_func=lambda word: "[" + word.upper() + "]")
wf.add_word("spoiler")
print(wf.filter("This is a spoiler."))  # Output: This is a [SPOILER].
```

## Working with Files

-----

```python
# Load words from a .txt or .json file (one word per line)
wf.load_from_file("banned_words.txt")

# Load words from URL (json or plain/text Content-Type)
wf.load_from_url("https://your_url/goes_here.json")

# Save the current word list
wf.save_to_file("output_words.txt")
```

## License

-----

This project is licensed under the MIT License.
See [LICENSE](https://github.com/VariableIsUndefined/wordfilter2/blob/master/LICENSE.md) for details.


-----

> Clean content made simple with **wordfilter2**.