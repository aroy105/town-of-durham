from app.game.phases import Phase
from app.game.state import GameState


class PhaseError(Exception):
    pass


def advance_phase(state: GameState, actor_token: str) -> None:
    if actor_token != state.host_token:
        raise PhaseError("only the host can advance the phase")

    if state.phase == Phase.LOBBY:
        state.phase = Phase.DAY
        state.day_number = 1
    elif state.phase == Phase.DAY:
        state.phase = Phase.NIGHT
    elif state.phase == Phase.NIGHT:
        state.phase = Phase.DAY
        state.day_number += 1
