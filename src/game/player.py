from __future__ import annotations

from enum import Enum, auto


class Player(Enum):
    P1 = auto()
    P2 = auto()

    def next(self) -> Player:
        match self:
            case Player.P1:
                return Player.P2
            case Player.P2:
                return Player.P1
