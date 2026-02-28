import random


class Player:
    """Represents a football player."""
    def __init__(
        self,
        name: str,
        position: str,
        rating: int,
        stamina: int = 100,
        form: float = 1.0,
        potential: int = 0,
        number: int = 0,
        age: int = 0,
        nationality: str = "",
        market_value: int = 0,
        skill_moves: int = 0,
        weak_foot: int = 0,
        preferred_foot: str = "",
        **kwargs,   # absorb extra JSON fields
    ):
        self.name: str           = name
        self.position: str       = position
        self.rating: int         = rating
        self.stamina: int        = stamina
        self.form: float         = form
        self.potential: int      = potential if potential > 0 else rating + random.randint(2, 10)
        self.number: int         = number if number > 0 else random.randint(1, 99)
        self.age: int            = age if age > 0 else random.randint(18, 35)
        self.nationality: str    = nationality

        self.market_value: int   = market_value if market_value > 0 else self._estimate_value()
        self.skill_moves: int    = skill_moves if skill_moves > 0 else random.randint(1, 5)
        self.weak_foot: int      = weak_foot if weak_foot > 0 else random.randint(1, 5)
        self.preferred_foot: str = preferred_foot if preferred_foot else random.choice(["Right", "Left"])

        self.career_goals = self.career_assists = self.career_apps = 0
        self.career_clean_sheets = self.career_yellow_cards = self.career_red_cards = 0

        self.goals = self.assists = self.yellow_cards = self.red_cards = 0
        self.injured = False
        self.matches_played = 0
        self.match_rating = 6.0
        self.tackles = self.passes_completed = self.dribbles = self.shots_taken = 0
        self.key_passes = self.interceptions = self.clearances = 0

    def _estimate_value(self) -> int:
        base = max(0, (self.rating - 60) * 2)
        age_mult = 1.5 if self.age <= 24 else (1.2 if self.age <= 28 else (0.8 if self.age <= 32 else 0.5))
        return max(1, round(base * age_mult))

    def get_effective_rating(self) -> float:
        """Calculate effective rating based on form and stamina."""
        return self.rating * self.form * (self.stamina / 100.0)

    def get_match_rating(self) -> float:
        """Calculate post-match rating (1.0-10.0) based on in-game stats."""
        base = 6.0
        base += self.goals * 1.2
        base += self.assists * 0.7
        base += self.key_passes * 0.15
        base += self.tackles * 0.12
        base += self.interceptions * 0.1
        base += self.passes_completed * 0.04
        base += self.dribbles * 0.08
        base -= self.yellow_cards * 0.4
        base -= self.red_cards * 1.8
        base += (self.stamina / 100.0 - 0.5) * 0.6
        return max(1.0, min(10.0, round(base, 1)))

    def get_position_full(self) -> str:
        return {
            "GK": "Goalkeeper", "DF": "Defender",
            "MF": "Midfielder", "FW": "Forward"
        }.get(self.position, self.position)

    def get_position_emoji(self) -> str:
        return {
            "GK": "🧤", "DF": "🛡️", "MF": "⚙️", "FW": "⚡"
        }.get(self.position, "⚽")

    def is_star_player(self) -> bool:
        return self.rating >= 88

    def development_potential(self) -> str:
        gap = self.potential - self.rating
        return "🌟 Elite" if gap >= 8 else ("⬆️ High" if gap >= 5 else ("📈 Some" if gap >= 2 else "🔒 Peak"))

    def get_value_str(self) -> str:
        return f"€{self.market_value}M"

    def get_form_label(self) -> str:
        return "🔥 Hot" if self.form >= 1.15 else ("😊 Good" if self.form >= 1.05 else ("😐 OK" if self.form >= 0.92 else ("😞 Poor" if self.form >= 0.80 else "❄️ Cold")))

    def reset_match_stats(self):
        """Reset match stats."""
        self.goals = self.assists = self.yellow_cards = self.red_cards = 0
        self.stamina = 100
        self.injured = False
        self.match_rating = 6.0
        self.tackles = self.passes_completed = self.dribbles = self.shots_taken = 0
        self.key_passes = self.interceptions = self.clearances = 0