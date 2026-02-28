import json
from typing import List

from models.team import Team
from models.player import Player

def load_teams(filepath: str = "data/teams.json") -> List[Team]:
    """Load teams from JSON file."""
    with open(filepath, "r", encoding="utf-8") as f:
        data = json.load(f)

    teams = []
    for t in data["teams"]:
        players = [Player(**p) for p in t["players"]]
        team_data = {k: v for k, v in t.items() if k != "players"}
        teams.append(Team(players=players, **team_data))
        
    return teams
