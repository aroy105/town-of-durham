from __future__ import annotations

from dataclasses import dataclass, field

from app.game.roles.base import AttackLevel, DefenseLevel


@dataclass
class NightContext:
    protections: dict[str, DefenseLevel] = field(default_factory=dict)
    pending_attacks: list[tuple[str, str, AttackLevel]] = field(default_factory=list)
    roleblocked: dict[str, str] = field(default_factory=dict)
    framed: set[str] = field(default_factory=set)
    doused: set[str] = field(default_factory=set)
    visits: list[tuple[str, str]] = field(default_factory=list)
    controlled: dict[str, str] = field(default_factory=dict)

    def grant_defense(self, token: str, level: DefenseLevel) -> None:
        current = self.protections.get(token, DefenseLevel.NONE)
        self.protections[token] = max(current, level)

    def queue_attack(self, source: str, target: str, attack: AttackLevel) -> None:
        self.pending_attacks.append((source, target, attack))

    def record_visit(self, visitor: str, target: str) -> None:
        self.visits.append((visitor, target))

    def control(self, controlled_token: str, redirect_to_token: str) -> None:
        self.controlled[controlled_token] = redirect_to_token
