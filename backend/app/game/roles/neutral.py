from __future__ import annotations

from typing import TYPE_CHECKING

from app.game.roles.base import (
    ActionResult,
    ActionSchema,
    ActionType,
    Alignment,
    AttackLevel,
    DefenseLevel,
    Faction,
    Role,
    basic_kill_night_action,
)

if TYPE_CHECKING:
    from app.game.night import NightContext
    from app.game.state import GameState, Player


class Arsonist(Role):
    id = "arsonist"
    display_name = "Arsonist"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_KILLING
    priority = 70
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        can_target_self=True,
        label="Douse",
    )
    flavor_text = "Douse targets in gas, then ignite them all at once."

    def __init__(self) -> None:
        super().__init__()
        self.doused_tokens: set[str] = set()

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        if target.token == actor.token:
            for doused_token in self.doused_tokens:
                ctx.queue_attack(actor.token, doused_token, AttackLevel.UNSTOPPABLE)
            message = f"You ignited {len(self.doused_tokens)} doused target(s)."
            self.doused_tokens.clear()
            return ActionResult(success=True, message=message)

        self.doused_tokens.add(target.token)
        ctx.doused.add(target.token)
        ctx.record_visit(actor.token, target.token)
        return ActionResult(success=True, message=f"You doused {target.display_name} in gas.")


class Survivor(Role):
    id = "survivor"
    display_name = "Survivor"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_BENIGN
    priority = 40
    max_uses = 4
    action_schema = ActionSchema(
        action_type=ActionType.PROTECTIVE,
        can_target_self=True,
        label="Vest",
    )
    flavor_text = "You just want to live. Use a bulletproof vest to protect yourself."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.grant_defense(actor.token, DefenseLevel.POWERFUL)
        self._consume_use()
        return ActionResult(success=True, message="You put on a bulletproof vest.")


class Werewolf(Role):
    id = "werewolf"
    display_name = "Werewolf"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_KILLING
    priority = 85
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Rampage",
    )
    flavor_text = "On full moon nights, you rampage through a target's home."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)
        is_full_moon = state.day_number % 3 == 0
        if not is_full_moon:
            return ActionResult(
                success=True, message=f"You watch {target.display_name}'s home quietly. No moon tonight."
            )

        ctx.queue_attack(actor.token, target.token, AttackLevel.UNSTOPPABLE)
        # TODO: a full-moon rampage should also hit everyone else who visited
        # target.token that night, not just the chosen target — needs the
        # finalized ctx.visits log after every other role resolves, same gap
        # as Veteran's counter-attack. Only the direct target is attacked
        # for now.
        return ActionResult(success=True, message=f"You rampage through {target.display_name}'s home!")

    def get_defense(self, state: GameState, player: Player) -> DefenseLevel:
        is_full_moon = state.day_number % 3 == 0
        return DefenseLevel.BASIC if is_full_moon else DefenseLevel.NONE


class SerialKiller(Role):
    id = "serial_killer"
    display_name = "Serial Killer"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_KILLING
    priority = 80
    defense = DefenseLevel.BASIC
    attack = AttackLevel.BASIC
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Kill",
    )
    flavor_text = "You want to kill everyone. Anyone who tries to roleblock you dies too — no restraint."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        return basic_kill_night_action(ctx, actor, target)

    def on_roleblocked(
        self, state: GameState, ctx: NightContext, actor: Player, roleblocker: Player
    ) -> ActionResult | None:
        ctx.queue_attack(actor.token, roleblocker.token, AttackLevel.BASIC)
        return ActionResult(
            success=True, message=f"You killed {roleblocker.display_name} for trying to stop you."
        )
        # NOTE: this hook is fully implemented and tested, but nothing calls
        # it automatically yet — the future resolver needs to check, for a
        # roleblocked actor, whether their role defines on_roleblocked and
        # call it (with ctx.roleblocked[actor.token] resolved to a Player)
        # instead of just skipping their action. Not wired up yet.


class Executioner(Role):
    id = "executioner"
    display_name = "Executioner"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_EVIL
    priority = 0
    action_schema = None
    flavor_text = "You want your target lynched by the town, by any means necessary."

    def __init__(self) -> None:
        super().__init__()
        self.target_token: str | None = None
        # TODO: needs (1) a win-condition check tied to `target_token`
        # specifically being lynched, not just dying, and (2) a hook that
        # fires when ANOTHER player dies (to convert to Jester if
        # target_token dies some other way) — on_death only covers your own
        # death today. Neither the win-condition system nor that hook exists
        # yet. Revisit once both are built.


class Witch(Role):
    id = "witch"
    display_name = "Witch"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_EVIL
    priority = 5
    action_schema = ActionSchema(
        action_type=ActionType.DECEPTION,
        num_targets=2,
        label="Control",
    )
    flavor_text = "Controls a target, forcing them to act on someone else instead."

    def night_action(
        self,
        state: GameState,
        ctx: NightContext,
        actor: Player,
        target: Player,
        secondary_target: Player | None = None,
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)

        if target.role is not None and target.role.control_immune:
            return ActionResult(success=False, message=f"{target.display_name} could not be controlled.")
        if secondary_target is None:
            return ActionResult(success=False, message="Witch requires a second target to redirect to.")

        ctx.control(target.token, secondary_target.token)
        return ActionResult(
            success=True,
            message=f"You controlled {target.display_name} to target {secondary_target.display_name}.",
        )
        # NOTE: this only records the redirect in ctx.controlled. Actually
        # overriding the controlled player's own night_action call to use
        # secondary_target instead of whatever they originally chose needs
        # real resolver support (checking ctx.controlled before invoking each
        # player's action) — not implemented yet since the resolver itself
        # doesn't exist. Also: the base can_target() only validates a single
        # `target` — secondary_target isn't validated at all here (e.g.
        # nothing stops picking an invalid or dead secondary_target). Worth
        # tightening once this is wired up to real gameplay.


class Jester(Role):
    id = "jester"
    display_name = "Jester"
    faction = Faction.NEUTRAL
    alignment = Alignment.NEUTRAL_EVIL
    priority = 0
    action_schema = None
    flavor_text = "You want to be lynched by the town."

    # NOTE: Jester's win condition (being lynched) and its "haunt" ability
    # (a one-time kill against whoever voted guilty, granted after being
    # lynched) both need systems that don't exist yet — the win-condition
    # checker, and a death-triggered hook to grant the haunt action. Same
    # deferred bucket as Executioner. Boilerplate only for now.
