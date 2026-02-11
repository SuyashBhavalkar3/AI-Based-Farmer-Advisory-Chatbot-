"""Models for translation module."""

from enum import Enum

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    MARATHI = "mr"
