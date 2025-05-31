#!/usr/bin/env python

from setuptools import setup

with open("README.md", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="wordfilter2",
    version="1.0.1",
    license="MIT",
    author="VariableIsUndefined",
    description="A simple word filter module for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/VariableIsUndefined/wordfilter2",
    python_requires=">=3.6",
    packages=["wordfilter2"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Communications",
        "Topic :: Text Processing :: Linguistic",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Development Status :: 5 - Production/Stable",
    ]
)