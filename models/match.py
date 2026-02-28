from typing import List, Optional
import random

from models.team import Team
from models.player import Player

WEATHER_OPTIONS = [
    "☀️ Sunny", "🌧️ Rainy", "💨 Windy", "❄️ Snowy",
    "⛅ Overcast", "🔥 Hot", "🌫️ Foggy", "🌩️ Stormy"
]


class Match:
    """Tracks single match state."""
    def __init__(self, team1: Team, team2: Team):
        self.team1: Team = team1
        self.team2: Team = team2

        self.score1 = self.score2 = 0
        self.possession1 = self.possession2 = 0
        self.shots1 = self.shots2 = self.shots_on_target1 = self.shots_on_target2 = 0
        self.fouls1 = self.fouls2 = 0
        self.corners1 = self.corners2 = self.offsides1 = self.offsides2 = 0
        self.assists1 = self.assists2 = 0
        self.xg1 = self.xg2 = 0.0
        self.big_chances1 = self.big_chances2 = 0
        self.pass_accuracy1 = self.pass_accuracy2 = 0
        self.dribbles1 = self.dribbles2 = self.tackles1 = self.tackles2 = 0
        self.interceptions1 = self.interceptions2 = self.clearances1 = self.clearances2 = 0
        self.key_passes1 = self.key_passes2 = 0

        self.momentum1: float = 50.0
        self.momentum2: float = 50.0

        self.events: List[str] = []
        self.current_minute: int = 0
        self.penalties: bool = False
        self.pens_score1: int = 0
        self.pens_score2: int = 0
        self.man_of_match: Optional[Player] = None
        self.weather: str = random.choice(WEATHER_OPTIONS)
        self.var_decisions: List[str] = []
        self.substitutions: List[str] = []
        self.scorers_list: List[tuple] = []

        team1.reset_match_state()
        team2.reset_match_state()

    def add_event(self, event: str):
        self.events.append(f"{self.current_minute}' {event}" if self.current_minute > 0 else event)

    def get_yellow_cards(self, team: Team) -> int:
        return sum(1 for p in team.players if p.yellow_cards >= 1)

    def get_red_cards(self, team: Team) -> int:
        return sum(p.red_cards for p in team.players)

    def get_total_assists(self, team: Team) -> int:
        return sum(p.assists for p in team.players)

    def get_player_ratings(self, team: Team) -> List[tuple]:
        ratings = [(p, p.get_match_rating()) for p in team.players]
        return sorted(ratings, key=lambda x: x[1], reverse=True)

    def get_pass_accuracy(self, team: Team) -> int:
        total_passes = sum(p.passes_completed for p in team.players)
        possession = self.possession1 if team == self.team1 else self.possession2
        attempted = max(1, possession * 2)
        return min(99, round(total_passes / attempted * 100))

    def get_xg(self, team: Team) -> float:
        return round(self.xg1 if team == self.team1 else self.xg2, 2)

    def get_momentum(self, team: Team) -> float:
        return self.momentum1 if team == self.team1 else self.momentum2

    def shift_momentum(self, towards_team: Team, amount: float = 5.0):
        """Shift momentum towards a specific team."""
        if towards_team == self.team1:
            self.momentum1, self.momentum2 = min(85, self.momentum1 + amount), max(15, self.momentum2 - amount)
        else:
            self.momentum1, self.momentum2 = max(15, self.momentum1 - amount), min(85, self.momentum2 + amount)

    def finalize_match(self):
        """Calculate final match consequences (ratings, Elo, morale)."""
        for p in self.team1.players + self.team2.players:
            p.match_rating = p.get_match_rating()
            p.matches_played += 1

        all_players = self.team1.players + self.team2.players
        self.man_of_match = max(all_players, key=lambda p: p.match_rating)

        self.pass_accuracy1 = self.get_pass_accuracy(self.team1)
        self.pass_accuracy2 = self.get_pass_accuracy(self.team2)

        if self.penalties:
            result1 = 1 if self.pens_score1 > self.pens_score2 else 0
        else:
            result1 = 1 if self.score1 > self.score2 else (0 if self.score1 < self.score2 else 0.5)
        
        result2 = 1 - result1

        expected1 = 1 / (1 + 10 ** ((self.team2.elo - self.team1.elo) / 400))
        self.team1.elo += round(32 * (result1 - expected1))
        self.team2.elo += round(32 * (result2 - (1 - expected1)))

        outcome1 = "win" if result1 == 1 else ("loss" if result1 == 0 else "draw")
        outcome2 = "win" if result2 == 1 else ("loss" if result2 == 0 else "draw")
        self.team1.update_morale(outcome1)
        self.team2.update_morale(outcome2)

        self.team1.update_chemistry()
        self.team2.update_chemistry()

        if result1 == 1:
            self.team1.wins += 1; self.team2.losses += 1
        elif result1 == 0:
            self.team1.losses += 1; self.team2.wins += 1
        else:
            self.team1.draws += 1; self.team2.draws += 1

        self.team1.goals_for     += self.score1
        self.team1.goals_against += self.score2
        self.team2.goals_for     += self.score2
        self.team2.goals_against += self.score1