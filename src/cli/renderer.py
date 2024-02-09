from ..game import (
    BOARD_SIZE,
    Action,
    Player,
    Result,
    State,
)
from ._envs import IS_TESTING

LINE = "-" * (4 * BOARD_SIZE + 1)


def read_action(state: State) -> Action:
    while True:
        if not IS_TESTING:
            print("Player ", end="")
            match state.player_to_act:
                case Player.P1:
                    print("1", end="")
                case Player.P2:
                    print("2", end="")
            print(" action? {", end="")
            for i, act in enumerate(state.all_actions):
                if i != 0:
                    print(", ", end="")
                print(f"{act}", end="")
            print("}: ", end="")

        col_input = input()

        try:
            col = int(col_input)
        except ValueError:
            print("you should enter a nonnegative integer!")
            continue

        try:
            action = Action.new(state=state, col=col)
        except Exception:
            print("invalid action for the current state!")
            continue

        return action


def print_state(state: State):
    if IS_TESTING:
        return

    print()
    print(LINE)
    print("|", end="")
    for cell in state.board:
        match cell:
            case Player.P1:
                print(" 1 |", end="")
            case Player.P2:
                print(" 2 |", end="")
            case None:
                print("   |", end="")
    print()
    print(LINE)


def print_result(result: Result, orig_state: State):
    match result:
        case Result.WIN:
            print("Player ", end="")
            match orig_state.player_to_act:
                case Player.P1:
                    print("1", end="")
                case Player.P2:
                    print("2", end="")
            print(" wins!")
        case Result.DRAW:
            print("draw!")
        case Result.WAITING_NEXT_ACTION:
            pass
