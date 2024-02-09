from __future__ import annotations

from ..game import BOARD_SIZE, Player, State

PLAYER_ENCODING: dict[Player | None, int] = {
    Player.P1: 0b01,
    Player.P2: 0b10,
    None: 0b00,
}

PLAYER_DECODING = {v: k for k, v in PLAYER_ENCODING.items()}


class EncodedState(int):
    def __str__(self) -> str:
        result = ""
        for i in reversed(range(BOARD_SIZE)):
            player = PLAYER_DECODING[self & 0b11]
            self >>= 2

            match player:
                case Player.P1:
                    result = "1" + result
                case Player.P2:
                    result = "2" + result
                case None:
                    result = "_" + result
            if i != 0:
                result = "," + result
        return result

    @staticmethod
    def new(state: State) -> EncodedState:
        result = 0
        # note: state.board[0] is the most significant bit
        for player in state.board:
            result = (result << 2) + PLAYER_ENCODING[player]
        return EncodedState(result)
