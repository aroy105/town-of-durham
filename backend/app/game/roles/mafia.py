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

class Mafioso(Role):
    id = "mafioso"
    display_name = "Mafioso"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
    priority = 80
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Kill",
    )
    flavor_text = "Carry out the Godfather's orders"

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        return basic_kill_night_action(ctx, actor, target)


class Godfather(Role):
    id = "godfather"
    display_name = "Godfather"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
    priority = 80
    defense = DefenseLevel.BASIC
    detection_immune = True
    action_schema = ActionSchema(
        action_type=ActionType.KILLING,
        label="Kill",
    )
    flavor_text = "Leader of the Mafia. Orders the killing of a townsperson each night."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        return basic_kill_night_action(ctx, actor, target)


class Framer(Role):
    id = "framer"
    display_name = "Framer"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
    priority = 20
    action_schema = ActionSchema(
        action_type=ActionType.DECEPTION,
        label="Frame",
    )
    flavor_text = "Frames a target to appear suspicious to investigation tonight."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.framed.add(target.token)
        ctx.record_visit(actor.token, target.token)
        return ActionResult(success=True, message=f"You framed {target.display_name}.")


class Consort(Role):
    id = "consort"
    display_name = "Consort"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
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


# Per-role exact-reveal flavor text. Uses our actual role names (Escort,
# Consort) in place of the wiki's alternate names (Tavern Keeper, Bootlegger)
# for consistency with the rest of the UI — flag if that substitution is
# wrong and you'd rather keep the original wording.
CONSIGLIERE_RESULTS: dict[str, str] = {
    "bodyguard": "Your target is a trained protector. They must be a Bodyguard.",
    "doctor": "Your target is a professional surgeon. They must be a Doctor.",
    "escort": "Your target is a beautiful person working for the town. They must be an Escort.",
    "investigator": "Your target gathers information about people. They must be an Investigator.",
    "jailer": "Your target detains people at night. They must be a Jailer.",
    "lookout": "Your target watches who visits people at night. They must be a Lookout.",
    "mayor": "Your target is the leader of the town. They must be the Mayor.",
    "medium": "Your target speaks with the dead. They must be a Medium.",
    "retributionist": "Your target wields mystical powers. They must be a Retributionist.",
    "sheriff": "Your target is a protector of the town. They must be a Sheriff.",
    "spy": "Your target secretly watches who someone visits. They must be a Spy.",
    "transporter": "Your target specializes in transportation. They must be a Transporter.",
    "vampire_hunter": "Your target tracks Vampires. They must be a Vampire Hunter!",
    "veteran": "Your target is a paranoid war hero. They must be a Veteran.",
    "vigilante": "Your target will bend the law to enact justice. They must be a Vigilante.",
    "ambusher": "Your target lies in wait. They must be an Ambusher.",
    "blackmailer": "Your target uses information to silence people. They must be a Blackmailer.",
    "consigliere": "Your target gathers information for the Mafia. They must be a Consigliere.",
    "consort": "Your target is a beautiful person working for the Mafia. They must be a Consort.",
    "disguiser": "Your target makes other people appear to be someone they're not. They must be a Disguiser.",
    "forger": "Your target is good at forging documents. They must be a Forger.",
    "framer": "Your target has a desire to deceive. They must be a Framer!",
    "godfather": "Your target is the leader of the Mafia. They must be the Godfather.",
    "hypnotist": "Your target is skilled at disrupting others. They must be a Hypnotist.",
    "janitor": "Your target cleans up dead bodies. They must be a Janitor.",
    "mafioso": "Your target does the Godfather's dirty work. They must be a Mafioso.",
    "amnesiac": "Your target does not remember their role. They must be an Amnesiac.",
    "arsonist": "Your target likes to watch things burn. They must be an Arsonist.",
    "executioner": "Your target wants someone to be lynched at any cost. They must be an Executioner.",
    "jester": "Your target wants to be lynched. They must be a Jester.",
    "serial_killer": "Your target wants to kill everyone. They must be a Serial Killer.",
    "survivor": "Your target simply wants to live. They must be a Survivor.",
    "vampire": "Your target drinks blood. They must be a Vampire!",
    "werewolf": "Your target howls at the moon. They must be a Werewolf.",
    "witch": "Your target casts spells on people. They must be a Witch.",
}


class Consigliere(Role):
    id = "consigliere"
    display_name = "Consigliere"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
    priority = 60
    action_schema = ActionSchema(
        action_type=ActionType.INVESTIGATIVE,
        label="Investigate",
    )
    flavor_text = "Investigates a target to learn their exact role."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)
        role_id = target.role.id if target.role else None
        message = CONSIGLIERE_RESULTS.get(role_id, "Your target's role could not be determined.")
        return ActionResult(success=True, message=message, effects={"role_id": role_id})


class Forger(Role):
    id = "forger"
    display_name = "Forger"
    faction = Faction.MAFIA
    alignment = Alignment.MAFIA
    priority = 20
    action_schema = ActionSchema(
        action_type=ActionType.DECEPTION,
        label="Forge",
    )
    flavor_text = "Forges a target's last will, altering what the town sees when they die."

    def night_action(
        self, state: GameState, ctx: NightContext, actor: Player, target: Player
    ) -> ActionResult:
        ctx.record_visit(actor.token, target.token)
        # TODO: actually alter target's Last Will once that feature exists on
        # Player — this currently only records the visit, no forging effect
        # is applied yet. Revisit once Last Will is built.
        return ActionResult(success=True, message=f"You forged {target.display_name}'s last will.")