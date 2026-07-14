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
    roleblock_night_action,
)

if TYPE_CHECKING:
    from app.game.night import NightContext
    from app.game.state import GameState, Player


# Investigator's result groups: each group is an ordered tuple of role ids
# that all produce the same flavor-text result, so the result never
# definitively reveals one role. Order is preserved (not a set) so the
# "X is a Y, Z, or W" line below can list them in a stable order. Includes
# roles not implemented yet (bodyguard, blackmailer, transporter, mayor,
# amnesiac, vampire, disguiser, janitor, retributionist, vampire_hunter) —
# the grouping logic doesn't care whether a Role class exists for an id,
# only whether it matches.
INVESTIGATOR_GROUPS: list[tuple[tuple[str, ...], str]] = [
    (("bodyguard", "godfather", "arsonist"), "Your target is not afraid to get their hands dirty."),
    (("vigilante", "veteran", "mafioso"), "Your target owns weapons."),
    (("spy", "blackmailer", "jailer"), "Your target knows your darkest secrets."),
    (("escort", "transporter", "consort"), "Your target is skilled at disrupting others."),
    (("investigator", "consigliere", "mayor"), "Your target has sensitive information to reveal."),
    (("sheriff", "executioner", "werewolf"), "Your target is waiting for the perfect moment to strike."),
    (("lookout", "forger", "amnesiac"), "Your target sticks to the shadows."),
    (("framer", "vampire", "jester"), "Your target may not be what they seem."),
    (("doctor", "disguiser", "serial_killer"), "Your target is covered in blood."),
    (("medium", "janitor", "retributionist"), "Your target works with dead bodies."),
    (("survivor", "vampire_hunter", "witch"), "Your target keeps to themselves."),
]

# Index of the group that a doused (Arsonist) or framed (Framer) target
# should also match, even if their actual role isn't in that group.
_DOUSED_GROUP_INDEX = 0
_FRAMED_GROUP_INDEX = 7


def _display_name_for_role_id(role_id: str) -> str:
    return role_id.replace("_", " ").title()


def _possible_roles_line(target_name: str, role_ids: tuple[str, ...]) -> str:
    names = [_display_name_for_role_id(rid) for rid in role_ids]
    if len(names) == 1:
        return f"{target_name} is a {names[0]}."
    return f"{target_name} is a {', '.join(names[:-1])}, or {names[-1]}."


class Doctor(Role):
    id = "doctor"
    display_name = "Doctor"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 40
    action_schema = ActionSchema(
        action_type=ActionType.PROTECTIVE,
        label="Heal",
    )
    flavor_text = "Heals one person each night, protecting them from an attack."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.grant_defense(target.token, DefenseLevel.POWERFUL)
        ctx.record_visit(actor.token, target.token)
        return ActionResult(success=True, message=f"You healed {target.display_name}.")

class Sheriff(Role):
    id = "sheriff"
    display_name = "Sheriff"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 60
    action_schema = ActionSchema(
        action_type=ActionType.INVESTIGATIVE,
        label="Interrogate",
    )
    flavor_text = "Check one person each night for suspicious activity."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)
        role = target.role
        is_suspicious = target.token in ctx.framed or (
            role is not None
            and not role.detection_immune
            and role.alignment in (Alignment.MAFIA, Alignment.NEUTRAL_KILLING)
        )

        message = (
            f"{target.display_name} is Suspicious!"
            if is_suspicious
            else f"{target.display_name} is Not Suspicious!"
        )

        return ActionResult(success=True, message=message, effects={"suspicious": is_suspicious})


class Investigator(Role):
    id = "investigator"
    display_name = "Investigator"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 60
    action_schema = ActionSchema(
        action_type=ActionType.INVESTIGATIVE,
        label="Investigate",
    )
    flavor_text = "Investigates a target, narrowing their role down to a group of possibilities."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)
        role_id = target.role.id if target.role else None

        for index, (role_ids, message) in enumerate(INVESTIGATOR_GROUPS):
            role_matches = role_id in role_ids
            doused_override = index == _DOUSED_GROUP_INDEX and target.token in ctx.doused
            framed_override = index == _FRAMED_GROUP_INDEX and target.token in ctx.framed
            if role_matches or doused_override or framed_override:
                full_message = f"{message} {_possible_roles_line(target.display_name, role_ids)}"
                return ActionResult(
                    success=True,
                    message=full_message,
                    effects={"group": index, "possible_roles": list(role_ids)},
                )

        return ActionResult(
            success=True,
            message="Your target's role could not be determined.",
            effects={"group": None},
        )


class Escort(Role):
    id = "escort"
    display_name = "Escort"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 10
    action_schema = ActionSchema(
        action_type=ActionType.SUPPORT,
        label="Roleblock",
    )
    flavor_text = "Distracts a target for the night, preventing them from using their ability."
    
    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        return roleblock_night_action(ctx, actor, target)


class Medium(Role):
    id = "medium"
    display_name = "Medium"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 0
    action_schema = None
    flavor_text = "You can communicate with the dead."

    # NOTE: Medium's real ability is passive — seeing dead chat (and,
    # in some rulesets, a once-per-game seance) while still alive. That's a
    # chat-visibility exception, not a targeted night action, so it can't be
    # expressed here at all. Needs ChatManager support once the chat system
    # (M7) exists — this class is boilerplate until then.


class Vigilante(Role):
    id = "vigilante"
    display_name = "Vigilante"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 80
    max_uses = 3
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Shoot",
    )
    flavor_text = "You have a gun and 3 bullets. Use them wisely."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        result = basic_kill_night_action(ctx, actor, target)
        self._consume_use()
        return result
        # TODO: if target turns out to be Town-aligned, Vigilante should feel
        # guilt and die the following night. That's a deferred, engine-level
        # special case (same bucket as Serial Killer killing its roleblocker)
        # — needs the resolver to check the victim's alignment after this
        # kill resolves and schedule a self-kill. Not implemented yet.


class Spy(Role):
    id = "spy"
    display_name = "Spy"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 90
    action_schema = ActionSchema(
        action_type=ActionType.INVESTIGATIVE,
        visits=False,
        label="Bug",
    )
    flavor_text = "Detects Mafia activity without leaving home."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        # Priority 90 is deliberate: this must resolve after every Mafia
        # role's tier (including the killing tier at 80) so ctx.visits is
        # fully populated with any Mafia visit to `target` before we read it.
        was_visited_by_mafia = False
        for visitor_token, visited_token in ctx.visits:
            if visited_token != target.token:
                continue
            visitor = state.get_player(visitor_token)
            if visitor and visitor.role and visitor.role.faction == Faction.MAFIA:
                was_visited_by_mafia = True
                break

        message = (
            f"Mafia activity detected around {target.display_name}."
            if was_visited_by_mafia
            else f"No Mafia activity detected around {target.display_name}."
        )
        # TODO: real Spy also reads the Mafia's private night chat/whispers —
        # that's a chat-system feature (M7), not something a night_action can
        # express. Revisit once chat exists.
        return ActionResult(success=True, message=message, effects={"mafia_visited": was_visited_by_mafia})


class Veteran(Role):
    id = "veteran"
    display_name = "Veteran"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 5
    max_uses = 3
    action_schema = ActionSchema(
        action_type=ActionType.SUPPORT,
        can_target_self=True,
        label="Alert",
    )
    flavor_text = "A war-hardened veteran. Go on alert to defend your home, but be cautious who you let in."

    def __init__(self) -> None:
        super().__init__()
        self.on_alert = False

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        self.on_alert = True
        self._consume_use()
        return ActionResult(success=True, message="You are on alert tonight.")
        # TODO: while on alert, Veteran should also counter-attack (Unstoppable)
        # anyone who visits them. That needs the FULL night's ctx.visits log,
        # which isn't final until every other visiting role has resolved —
        # needs a dedicated "post-visits" pass in the future resolver. Only
        # the defense (via get_defense below) is implemented for now.

    def get_defense(self, state: GameState, player: Player) -> DefenseLevel:
        return DefenseLevel.POWERFUL if self.on_alert else DefenseLevel.NONE

    def reset_for_night(self) -> None:
        self.on_alert = False


class Lookout(Role):
    id = "lookout"
    display_name = "Lookout"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 90
    action_schema = ActionSchema(
        action_type=ActionType.INVESTIGATIVE,
        label="Watch",
    )
    flavor_text = "Watches a target's house to see who visits them at night."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        # Priority 90, same reasoning as Spy: must resolve after every other
        # visiting role (including the killing tier at 80) so ctx.visits is
        # fully populated before we read it.
        ctx.record_visit(actor.token, target.token)

        visitor_names: list[str] = []
        for visitor_token, visited_token in ctx.visits:
            if visited_token != target.token or visitor_token == actor.token:
                continue
            visitor = state.get_player(visitor_token)
            if visitor is not None:
                visitor_names.append(visitor.display_name)

        message = (
            f"{', '.join(visitor_names)} visited {target.display_name} last night."
            if visitor_names
            else f"No one visited {target.display_name} last night."
        )
        return ActionResult(success=True, message=message, effects={"visitors": visitor_names})


class Jailer(Role):
    id = "jailer"
    display_name = "Jailer"
    faction = Faction.TOWN
    alignment = Alignment.TOWN
    priority = 10
    max_uses = 3
    day_action_schema = ActionSchema(
        action_type=ActionType.SUPPORT,
        label="Jail",
    )
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Interrogate",
    )
    flavor_text = "Detain a player during the day, then interrogate or execute them at night."

    def day_action(
        self, state: GameState, actor: Player, target: Player | None = None
    ) -> ActionResult:
        if target is None:
            state.jailed_token = None
            return ActionResult(success=True, message="You did not jail anyone tonight.")
        state.jailed_token = target.token
        return ActionResult(success=True, message=f"You have jailed {target.display_name}.")

    def night_action(
        self,
        state: GameState,
        ctx: NightContext,
        actor: Player,
        target: Player,
        execute: bool = False,
    ) -> ActionResult:
        # Jailer's roleblock overrides roleblock immunity entirely — unlike
        # roleblock_night_action(), this deliberately does not check
        # target.role.roleblock_immune. No record_visit here either: the
        # jailed player is taken to jail, not "visited" at their own home.
        ctx.roleblocked[target.token] = actor.token

        if not execute:
            return ActionResult(success=True, message=f"You interrogated {target.display_name}.")

        if state.day_number <= 1:
            return ActionResult(success=False, message="You cannot execute on the first night.")
        if actor.token in ctx.roleblocked:
            return ActionResult(success=False, message="You were roleblocked and could not execute.")

        ctx.queue_attack(actor.token, target.token, AttackLevel.UNSTOPPABLE)
        self._consume_use()
        return ActionResult(success=True, message=f"You executed {target.display_name}.")
        # TODO: executing a Town-aligned player should permanently disable
        # further executions (per real Jailer rules) — needs
        # alignment-checking after a kill resolves, same deferred bucket as
        # Vigilante's guilt mechanic. Not implemented yet.
        # TODO: the private Jailer <-> jailed-player night chat, and the
        # Mafia/Vampire "hauled off to jail" notification in their faction
        # chat, are both chat-system features (M7) — not something a Role
        # class can express. Revisit once chat exists.