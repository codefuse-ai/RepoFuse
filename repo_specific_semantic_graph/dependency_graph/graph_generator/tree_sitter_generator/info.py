from __future__ import annotations

from dataclasses import dataclass


@dataclass
class ParseTreeInfo:
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    text: str
    type: str
    parent: ParseTreeInfo | None = None


@dataclass
class RegexInfo:
    start_point: tuple[int, int]
    end_point: tuple[int, int]
    text: str
