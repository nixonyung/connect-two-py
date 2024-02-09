from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto

from ._envs import BOARD_SIZE
from .player import Player


@dataclass(frozen=True, slots=True, eq=True, order=True)
class Action:
    col: int

    def __str__(self) -> str:
        return f"({self.col})"

    @staticmethod
    def new(state: State, col: int) -> Action:
        action = Action(col=col)
        if action not in state.all_actions:
            raise Exception("Action.new: action is invalid for the given state")
        return action


class Result(Enum):
    WIN = auto()
    DRAW = auto()
    WAITING_NEXT_ACTION = auto()


Cell = Player | None


#
# loosely following [gymnasium.Env](https://gymnasium.farama.org/api/env/)
#
# (ref.) [UsingSlots](https://wiki.python.org/moin/UsingSlots)
# (ref.) [Providing Read-Only Attributes](https://realpython.com/python-property/#providing-read-only-attributes)
# (ref.) [What is the difference between @staticmethod and @classmethod in Python?](https://stackoverflow.com/questions/136097/what-is-the-difference-between-staticmethod-and-classmethod-in-python)
# (ref.) [How do I type hint a method with the type of the enclosing class?](https://stackoverflow.com/questions/33533148/how-do-i-type-hint-a-method-with-the-type-of-the-enclosing-class)
#
@dataclass(frozen=True, slots=True)
class State:
    board: tuple[Cell, ...]
    player_to_act: Player

    @property
    def all_actions(self):
        return (Action(col=col) for col, cell in enumerate(self.board) if cell is None)

    def step(self, action: Action) -> tuple[State, Result]:
        new_state = State(
            board=tuple(
                self.player_to_act if col == action.col else orig_cell
                for col, orig_cell in enumerate(self.board)
            ),
            player_to_act=self.player_to_act.next(),
        )

        result: Result
        if action.col > 0 and new_state.board[action.col - 1] is self.player_to_act:
            result = Result.WIN
        elif action.col < BOARD_SIZE - 1 and new_state.board[action.col + 1] is self.player_to_act:
            result = Result.WIN
        elif next(new_state.all_actions, None) is None:
            result = Result.DRAW
        else:
            result = Result.WAITING_NEXT_ACTION

        return new_state, result


INITIAL_STATE = State(
    board=(None,) * BOARD_SIZE,
    player_to_act=Player.P1,
)
