from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum

from ..game import Result
from .encoding import EncodedState


#
# note: only implemented comparisons with Value itself
#
# (ref.) [Can I use an Enum with floating point values and comparators in Python 3.9 and still leverage the efficiency of numpy operations?](https://stackoverflow.com/questions/69716107/can-i-use-an-enum-with-floating-point-values-and-comparators-in-python-3-9-and-s)
#
# (alt.) [Decimal Python vs. float runtime](https://stackoverflow.com/questions/41453307/decimal-python-vs-float-runtime)
#   - but using Decimal is slower
# (alt.) [@functools.total_ordering](https://docs.python.org/3/library/functools.html)
#   - but using functools.total_ordering is slower
#
class Value(Enum):
    # (ref.) [How to implement negative infinity in python?](https://stackoverflow.com/questions/15170267/how-to-implement-negative-infinity-in-python)
    UNDEFINED = -math.inf
    WIN = 1.0
    LOSE = -1.0
    DRAW = 0.0

    def __eq__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__eq__: invalid rhs {type(rhs)=}")
        # (ref.) [What is the best way to compare floats for almost-equality in Python?](https://stackoverflow.com/questions/5595425/what-is-the-best-way-to-compare-floats-for-almost-equality-in-python)
        return math.isclose(self.value, rhs.value)

    def __ne__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__ne__: invalid rhs {type(rhs)=}")
        return not math.isclose(self.value, rhs.value)

    def __lt__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__lt__: invalid rhs {type(rhs)=}")
        return not math.isclose(self.value, rhs.value) and self.value < rhs.value

    def __le__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__le__: invalid rhs {type(rhs)=}")
        return math.isclose(self.value, rhs.value) or self.value < rhs.value

    def __gt__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__gt__: invalid rhs {type(rhs)=}")
        return not math.isclose(self.value, rhs.value) and self.value > rhs.value

    def __ge__(self, rhs: object) -> bool:
        if not isinstance(rhs, Value):
            raise Exception(f"Value.__ge__: invalid rhs {type(rhs)=}")
        return math.isclose(self.value, rhs.value) or self.value > rhs.value


# Reward stores the value and thus is subject to be trained
@dataclass(slots=True)
class Reward:
    # what the agent knows must happen:
    to_encoded_state: EncodedState
    result: Result

    # what the agent thinks will happen:c
    value: Value = field(default_factory=lambda: Value.UNDEFINED)

    # note: curr_epoch should start from 1
    last_visited_at: int = 0
