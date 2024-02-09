from __future__ import annotations

from collections import defaultdict

from ..game import INITIAL_STATE, Action, Player, Result, State
from .encoding import EncodedState
from .reward import Reward, Value

StateAction = tuple[EncodedState, Action]


class Agent(
    defaultdict[
        EncodedState,
        dict[Action, Reward],
    ]
):
    # (ref.) [How can I inherit defaultdict and use its copy method in subclass method?](https://stackoverflow.com/questions/45410638/how-can-i-inherit-defaultdict-and-use-its-copy-method-in-subclass-method)
    def __init__(self):
        super().__init__(dict)

    # (ref.) [What is the difference between __str__ and __repr__?](https://stackoverflow.com/questions/1436703/what-is-the-difference-between-str-and-repr)
    def __str__(self) -> str:
        lines = [""] * len(self)
        for i, encoded_state in enumerate(sorted(self)):
            optimal_actions = sorted(self.optimal_actions(at_encoded_state=encoded_state))
            max_value = self.reward(encoded_state, optimal_actions[0]).value

            lines[
                i
            ] = f"{str(encoded_state)} [{max_value}] -> {{{', '.join(str(act) for act in optimal_actions)}}}"
        return "\n".join(lines)

    def reward(
        self,
        at_encoded_state: EncodedState,
        action: Action,
    ) -> Reward:
        return self[at_encoded_state][action]

    def max_value(
        self,
        at_encoded_state: EncodedState,
    ):
        return max(self[at_encoded_state].values(), key=lambda r: r.value).value

    def optimal_actions(
        self,
        at_encoded_state: EncodedState,
    ):
        return (
            action
            for action, reward in self[at_encoded_state].items()
            if reward.value == self.max_value(at_encoded_state=at_encoded_state)
        )

    @staticmethod
    def __init_agents(
        p1_agent: Agent,
        p2_agent: Agent,
    ):
        # BFS
        # ASSUMPTION: there are no loops in states, i.e. the state-space is a one-way tree without loops
        curr_player = Player.P1
        unexplored: set[
            tuple[
                State,
                EncodedState,  # OPTIMIZATION: reuse encoded_state during exploring
            ]
        ] = set(
            [
                (
                    INITIAL_STATE,
                    EncodedState.new(state=INITIAL_STATE),
                ),
            ]
        )
        while unexplored:
            curr_agent: Agent
            match curr_player:
                case Player.P1:
                    curr_agent = p1_agent
                case Player.P2:
                    curr_agent = p2_agent

            new_unexplored: set[tuple[State, EncodedState]] = set()
            for s, encoded_s in unexplored:
                for act in s.all_actions:
                    s_next, result = s.step(action=act)
                    encoded_s_next = EncodedState.new(state=s_next)

                    # init agent
                    curr_agent[encoded_s][act] = Reward(
                        to_encoded_state=encoded_s_next,
                        result=result,
                    )
                    match result:
                        case Result.WIN:
                            curr_agent[encoded_s][act].value = Value.WIN
                        case Result.DRAW:
                            curr_agent[encoded_s][act].value = Value.DRAW
                        case Result.WAITING_NEXT_ACTION:
                            new_unexplored.add((s_next, encoded_s_next))

            unexplored = new_unexplored
            curr_player = curr_player.next()

    @staticmethod
    def __backtrack(
        agent: Agent,
        trajectory: list[StateAction],
        value: Value,
        curr_epoch: int,
    ):
        has_update = False
        for state_action in reversed(trajectory):
            curr_reward = agent.reward(*state_action)
            if curr_reward.last_visited_at == curr_epoch:
                if value > curr_reward.value:
                    curr_reward.value = value
                    has_update = True
            else:
                if value != curr_reward.value:
                    curr_reward.value = value
                    has_update = True

            curr_reward.last_visited_at = curr_epoch

        # debug
        print(
            "backtracking...  ",
            f"[{value}]",
            tuple(
                f"{str(state_action[0])} -> {state_action[1].col}" for state_action in trajectory
            ),
            f"  ({has_update=})",
        )
        return has_update

    @staticmethod
    def __train(
        target: Agent,
        opponent: Agent,
        curr_epoch: int,
        initial_encoded_states: tuple[EncodedState, ...],
    ):
        # debug
        print()
        print(f"{curr_epoch = }:")

        has_update = False

        # DFS without recursion
        # (assuming that there is no loop in states, i.e. the state-space is a tree without loops)
        trajectory: list[StateAction] = []  # LIFO
        unexplored: list[  # LIFO
            tuple[
                StateAction,
                int,  # a helper state storing the previous trajectory length
            ]
        ] = list(
            ((s, act), 0)
            for s in initial_encoded_states
            for act in target.optimal_actions(at_encoded_state=s)
        )
        while unexplored:
            state_action, trajectory_len = unexplored.pop()
            trajectory = trajectory[:trajectory_len]
            trajectory.append(state_action)

            reward = target.reward(*state_action)
            v: Value | None = None
            # OPTIMIZATION: use the reward's value as is if the choice is already explored in this epoch
            if reward.last_visited_at == curr_epoch:
                v = reward.value
            else:
                match reward.result:
                    case Result.WIN:
                        v = Value.WIN
                    case Result.DRAW:
                        v = Value.DRAW
                    case _:
                        max_value = Value.UNDEFINED
                        s_next = reward.to_encoded_state
                        for reward_oppo in (
                            opponent.reward(at_encoded_state=s_next, action=act_oppo)
                            for act_oppo in opponent.optimal_actions(at_encoded_state=s_next)
                        ):
                            match reward_oppo.result:
                                case Result.WIN:
                                    max_value = max(max_value, Value.LOSE)
                                case Result.DRAW:
                                    max_value = max(max_value, Value.DRAW)
                                case _:
                                    s_next_next = reward_oppo.to_encoded_state
                                    unexplored.extend(
                                        ((s_next_next, act), len(trajectory))
                                        for act in target.optimal_actions(
                                            at_encoded_state=s_next_next
                                        )
                                    )
                        if max_value is not Value.UNDEFINED:
                            v = max_value
            if v is not None:
                if Agent.__backtrack(
                    agent=target,
                    trajectory=trajectory,
                    value=v,
                    curr_epoch=curr_epoch,
                ):
                    has_update = True
        return has_update

    @staticmethod
    def new_agents() -> tuple[Agent, Agent]:
        ENCODED_INITIAL_STATE = EncodedState.new(state=INITIAL_STATE)

        p1_agent = Agent()
        p2_agent = Agent()

        Agent.__init_agents(
            p1_agent=p1_agent,
            p2_agent=p2_agent,
        )

        curr_epoch = 0
        curr_player = Player.P1
        while True:
            curr_epoch += 1
            has_update: bool
            match curr_player:
                case Player.P1:
                    has_update = Agent.__train(
                        target=p1_agent,
                        opponent=p2_agent,
                        curr_epoch=curr_epoch,
                        initial_encoded_states=(ENCODED_INITIAL_STATE,),
                    )
                case Player.P2:
                    has_update = Agent.__train(
                        target=p2_agent,
                        opponent=p1_agent,
                        curr_epoch=curr_epoch,
                        initial_encoded_states=tuple(
                            p1_agent.reward(
                                at_encoded_state=ENCODED_INITIAL_STATE,
                                action=act,
                            ).to_encoded_state
                            for act in p1_agent.optimal_actions(
                                at_encoded_state=ENCODED_INITIAL_STATE
                            )
                        ),
                    )
            if not has_update:
                break
            # debug
            match curr_player:
                case Player.P1:
                    print(p1_agent)
                case Player.P2:
                    print(p2_agent)
            curr_player = curr_player.next()
        return p1_agent, p2_agent
