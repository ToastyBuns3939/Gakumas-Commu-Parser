from typing import NamedTuple


class RawLine(NamedTuple):
    group_type: str
    name: str
    text: str


class TranslationLine(NamedTuple):
    group_type: str
    name: str
    translated_name: str
    text: str
    translated_text: str
