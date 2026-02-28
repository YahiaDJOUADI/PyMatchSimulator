import os
import json
from models.match import Match

def save_match_history(match: Match, history_file: str = "data/matches.json"):
    """Save match history to JSON."""
    if not os.path.exists(history_file):
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump({"matches": []}, f, indent=2)

    with open(history_file, "r+", encoding="utf-8") as f:
        data = json.load(f)
        data["matches"].append({
            "team1":            match.team1.name,
            "team2":            match.team2.name,
            "score1":           match.score1,
            "score2":           match.score2,
            "penalties":        match.penalties,
            "pens_score1":      match.pens_score1 if match.penalties else None,
            "pens_score2":      match.pens_score2 if match.penalties else None,
            "weather":          match.weather,
            "motm":             match.man_of_match.name if match.man_of_match else None,
            "var_decisions":    len(match.var_decisions),
            "subs":             len(match.substitutions),
            "shots1":           match.shots1,
            "shots2":           match.shots2,
            "shots_on_target1": match.shots_on_target1,
            "shots_on_target2": match.shots_on_target2,
            "xg1":              round(match.xg1, 2),
            "xg2":              round(match.xg2, 2),
            "big_chances1":     match.big_chances1,
            "big_chances2":     match.big_chances2,
        })
        f.seek(0)
        json.dump(data, f, indent=2)
        f.truncate()

def update_career_stats(match: Match, stats_file: str = "data/stats.json"):
    """Update career stats for match players."""
    stats = {}
    if os.path.exists(stats_file):
        with open(stats_file, "r", encoding="utf-8") as f:
            stats = json.load(f)

    scorers       = stats.get("scorers", {})
    assists_dict  = stats.get("assists", {})
    clean_sheets  = stats.get("clean_sheets", {})
    apps          = stats.get("apps", {})

    for team in [match.team1, match.team2]:
        opposing_score = match.score2 if team == match.team1 else match.score1
        
        for p in team.players:
            if p.goals > 0:
                scorers[p.name] = scorers.get(p.name, 0) + p.goals
            if p.assists > 0:
                assists_dict[p.name] = assists_dict.get(p.name, 0) + p.assists
            apps[p.name] = apps.get(p.name, 0) + 1
            if p.position == "GK" and opposing_score == 0:
                clean_sheets[p.name] = clean_sheets.get(p.name, 0) + 1

    stats["scorers"]      = scorers
    stats["assists"]      = assists_dict
    stats["clean_sheets"] = clean_sheets
    stats["apps"]         = apps

    with open(stats_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2)
