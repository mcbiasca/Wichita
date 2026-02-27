from __future__ import annotations

import json
import os
from dataclasses import asdict, is_dataclass
from typing import Any, Dict

import pygame


def clamp(value: float, min_value: float, max_value: float) -> float:
    return max(min_value, min(value, max_value))


def vec2(value: tuple[float, float] | pygame.Vector2) -> pygame.Vector2:
    if isinstance(value, pygame.Vector2):
        return value
    return pygame.Vector2(value[0], value[1])


def distance(a: pygame.Vector2, b: pygame.Vector2) -> float:
    return (a - b).length()


def save_json(path: str, data: Dict[str, Any]) -> None:
    def _default(obj: Any) -> Any:
        if is_dataclass(obj):
            return asdict(obj)
        raise TypeError("Object is not JSON serializable")

    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=_default)


def load_json(path: str) -> Dict[str, Any] | None:
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as handle:
        return json.load(handle)
