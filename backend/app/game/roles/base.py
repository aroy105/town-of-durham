from __future__ import annotations

from abc import ABC
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.game.night import NightContext
    from app.game.state import GameState, Player


class Faction(str, Enum):
    TOWN = "town"
    MAFIA = "mafia"
    NEUTRAL = "neutral"


class Alignment(str, Enum):
    TOWN = "town"
    MAFIA = "mafia"
    NEUTRAL_KILLING = "neutral_killing"
    NEUTRAL_BENIGN = "neutral_benign"
    NEUTRAL_EVIL = "neutral_evil"
    NEUTRAL_CHAOS = "neutral_chaos"


class DefenseLevel(int, Enum):
    NONE = 0
    BASIC = 1
    POWERFUL = 2
    INVINCIBLE = 3


class AttackLevel(int, Enum):
    NONE = 0
    BASIC = 1
    POWERFUL = 2
    UNSTOPPABLE = 3


class ActionType(str, Enum):
    INVESTIGATIVE = "investigative"
    PROTECTIVE = "protective"
    KILLING = "killing"
    SUPPORT = "support"
    DECEPTION = "deception"
    NONE = "none"


class DeathCause(str, Enum):
    NIGHT_KILL = "night_kill"
    LYNCH = "lynch"


@dataclass(frozen=True)
class ActionSchema:
    action_type: ActionType
    num_targets: int = 1
    can_target_self: bool = False
    can_target_dead: bool = False
    visits: bool = True
    label: str = "Act"


@dataclass
class ActionResult:
    success: bool
    message: str = ""
    effects: dict[str, Any] = field(default_factory=dict)


class Role(ABC):
    id: str
    display_name: str
    faction: Faction
    alignment: Alignment
    priority: int = 0
    defense: DefenseLevel = DefenseLevel.NONE
    attack: AttackLevel = AttackLevel.NONE
    action_schema: ActionSchema | None = None
    day_action_schema: ActionSchema | None = None
    flavor_text: str = ""
    sprite_key: str = ""
    max_uses: int | None = None
    roleblock_immune: bool = False
    detection_immune: bool = False
    control_immune: bool = False
    unique_immunities: frozenset[str] = frozenset()

    def __init__(self) -> None:
        self.uses_remaining: int | None = self.max_uses

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        for attr in ("id", "display_name", "faction", "alignment"):
            if not hasattr(cls, attr):
                raise TypeError(f"{cls.__name__} is missing required Role attribute '{attr}'")

    def get_defense(self, state: GameState, player: Player) -> DefenseLevel:
        return self.defense

    def can_target(self, state: GameState, actor: Player, target: Player) -> bool:
        schema = self.action_schema
        if schema is None:
            return False
        if self.uses_remaining is not None and self.uses_remaining <= 0:
            return False
        if target.token == actor.token and not schema.can_target_self:
            return False
        if not target.alive and not schema.can_target_dead:
            return False
        if state.jailed_token is not None and target.token == state.jailed_token:
            return False
        return True

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        return ActionResult(success=False, message="no night action")

    def day_action(
        self, state: GameState, actor: Player, target: Player | None = None
    ) -> ActionResult:
        return ActionResult(success=False, message="no day action")

    def on_death(self, state: GameState, cause: DeathCause) -> None:
        return None

    def on_roleblocked(
        self, state: GameState, ctx: NightContext, actor: Player, roleblocker: Player
    ) -> ActionResult | None:
        return None

    def reset_for_night(self) -> None:
        return None

    def _consume_use(self) -> None:
        if self.uses_remaining is not None:
            self.uses_remaining -= 1


def roleblock_night_action(ctx: NightContext, actor: Player, target: Player) -> ActionResult:
    ctx.record_visit(actor.token, target.token)

    if target.role is not None and target.role.roleblock_immune:
        return ActionResult(success=False, message=f"{target.display_name} could not be roleblocked.")

    ctx.roleblocked[target.token] = actor.token
    return ActionResult(success=True, message=f"You roleblocked {target.display_name}.")


def basic_kill_night_action(ctx: NightContext, actor: Player, target: Player) -> ActionResult:
    ctx.queue_attack(actor.token, target.token, AttackLevel.BASIC)
    ctx.record_visit(actor.token, target.token)
    return ActionResult(success=True, message=f"You attacked {target.display_name}.")
