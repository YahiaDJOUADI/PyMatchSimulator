from typing import List, Optional

from models.player import Player


FORMATIONS = {
    "4-4-2":   (1.00, 1.00, 1.00),
    "4-3-3":   (1.15, 0.95, 0.90),
    "5-3-2":   (0.85, 1.00, 1.15),
    "3-5-2":   (1.05, 1.15, 0.80),
    "4-5-1":   (0.90, 1.20, 0.95),
    "4-2-3-1": (1.10, 1.05, 0.95),
    "3-4-3":   (1.20, 1.00, 0.75),
    "4-1-4-1": (0.95, 1.10, 1.05),
    "5-4-1":   (0.80, 1.10, 1.20),
    "4-4-2 Diamond": (1.08, 1.12, 0.92),
}


class Team:
    def __init__(
        self,
        name: str,
        attack: int,
        defense: int,
        midfield: int,
        players: List[Player],
        elo: Optional[int] = 1500,
        formation: str = "4-4-2",
        color: str = "#D4AF37",
    ):
        self.name: str = name
        self.attack: int = attack
        self.defense: int = defense
        self.midfield: int = midfield
        self.players: List[Player] = players
        self.elo: int = elo if elo is not None else 1500
        self.formation: str = formation
        self.color: str = color
        self.morale: float = 1.0
        self.chemistry: float = 1.0
        self.subs_made: int = 0
        self.overall_rating: float = self._calculate_overall()
        self.logo_path: str = f"assets/badges/{self.name.replace(' ', '_').lower()}.png"

        self.wins: int = 0
        self.draws: int = 0
        self.losses: int = 0
        self.goals_for: int = 0
        self.goals_against: int = 0

    def _calculate_overall(self) -> float:
        """Calculate overall rating."""
        return round((self.attack + self.defense + self.midfield) / 3.0, 1)

    @property
    def goal_difference(self) -> int:
        return self.goals_for - self.goals_against

    @property
    def matches_played(self) -> int:
        return self.wins + self.draws + self.losses

    @property
    def points(self) -> int:
        return self.wins * 3 + self.draws

    def get_tactical_bonus(self) -> tuple:
        return FORMATIONS.get(self.formation, (1.0, 1.0, 1.0))

    def get_active_players(self) -> List[Player]:
        return [p for p in self.players if not p.injured and not p.red_cards]

    def get_multiplier(self) -> float:
        """Calculate performance multiplier based on stamina, morale, and chemistry."""
        active = self.get_active_players()
        if not active:
            return 0.0
        avg_stamina = sum(p.stamina for p in active) / len(active) / 100.0
        player_penalty = (11 - min(11, len(active))) * 0.09
        morale_factor = max(0.5, min(1.5, self.morale))
        chemistry_factor = max(0.6, min(1.2, self.chemistry))
        return avg_stamina * (1 - player_penalty) * morale_factor * chemistry_factor

    def get_effective_attack(self) -> float:
        return self.attack * self.get_multiplier() * self.get_tactical_bonus()[0]

    def get_effective_defense(self) -> float:
        return self.defense * self.get_multiplier() * self.get_tactical_bonus()[2]

    def get_effective_midfield(self) -> float:
        return self.midfield * self.get_multiplier() * self.get_tactical_bonus()[1]

    def get_morale_label(self) -> str:
        return "🔥 Excellent" if self.morale >= 1.35 else ("😊 Good" if self.morale >= 1.15 else ("😐 Neutral" if self.morale >= 0.90 else ("😞 Low" if self.morale >= 0.70 else "😰 Crisis")))

    def update_morale(self, result: str):
        delta = 0.08 if result == "win" else (0.02 if result == "draw" else -0.06)
        self.morale = max(0.5, min(1.5, self.morale + delta))

    def update_chemistry(self):
        self.chemistry = min(1.2, self.chemistry + 0.02)

    def reset_match_state(self):
        self.subs_made = 0
        for p in self.players:
            p.reset_match_stats()