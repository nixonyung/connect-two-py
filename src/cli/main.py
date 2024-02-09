from ..game import INITIAL_STATE, Result
from .renderer import print_result, print_state, read_action


def main():
    state = INITIAL_STATE
    print_state(state=state)

    while True:
        action = read_action(state=state)
        next_state, result = state.step(action=action)
        print_state(state=next_state)
        print_result(result=result, orig_state=state)
        match result:
            case Result.WAITING_NEXT_ACTION:
                state = next_state
            case _:
                break
