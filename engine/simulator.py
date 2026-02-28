import random

from models.match import Match
from models.team import Team
from models.player import Player


from engine.commentary import (
    COMMENTARY_POOL, DRIBBLE_EVENTS, KEY_PASS_EVENTS, SHOT_THEMES,
    BIG_CHANCE_INTRO, GOAL_MESSAGES, BIG_CHANCE_GOAL, MISS_MESSAGES,
    BIG_CHANCE_MISS, CLEARANCE_EVENTS
)


class SimulatorEngine:
    def __init__(self, match: Match):
        self.match: Match = match

    def simulate_match(self):
        """Simulate full match."""
        self.match.add_event(f"{self.match.weather} conditions today at the stadium!")
        self.match.add_event("⚡ Kick-off! The match is underway.")
        self.match.current_minute = 0
        self.simulate_loop(45)
        self._halftime_summary()
        self.simulate_loop(90)
        if self.match.score1 == self.match.score2:
            self.match.add_event("⏱️ Full time — It's a draw! Going straight to extra time!")
            self.simulate_loop(105, is_extra=True)
            self.simulate_loop(120, is_extra=True)
            if self.match.score1 == self.match.score2:
                self.penalty_shootout()
        self.match.finalize_match()

    def _halftime_summary(self):
        poss_total = self.match.possession1 + self.match.possession2
        p1_pct = round(self.match.possession1 / poss_total * 100) if poss_total else 50
        self.match.add_event(
            f"🔔 HALF TIME — {self.match.team1.name} {self.match.score1} - "
            f"{self.match.score2} {self.match.team2.name} | "
            f"Possession: {p1_pct}% vs {100 - p1_pct}% | "
            f"Shots: {self.match.shots_on_target1} on target ({self.match.shots1} total) vs "
            f"{self.match.shots_on_target2} on target ({self.match.shots2} total) | "
            f"xG: {self.match.xg1:.1f} vs {self.match.xg2:.1f}"
        )

    def simulate_loop(self, max_minute: int, is_extra: bool = False):
        start = self.match.current_minute + 1
        for minute in range(start, max_minute + 1):
            self.match.current_minute = minute
            self.simulate_minute(is_extra=is_extra)

    def get_weather_modifiers(self):
        """Returns (foul_mod, shot_accuracy_mod, stamina_mod, xg_mod)."""
        weather = self.match.weather
        if "Rainy" in weather:
            return (0.04, -0.03, 0.0, -0.005)
        elif "Windy" in weather:
            return (0.0, -0.02, 0.0, -0.003)
        elif "Snowy" in weather:
            return (0.02, -0.04, 0.4, -0.008)
        elif "Foggy" in weather:
            return (0.02, -0.015, 0.1, -0.004)
        elif "Stormy" in weather:
            return (0.06, -0.05, 0.3, -0.01)
        elif "Hot" in weather:
            return (0.0, 0.0, 0.5, 0.0)
        else:
            return (0.0, 0.0, 0.0, 0.0)

    def simulate_minute(self, is_extra: bool = False):
        """Simulate a single minute."""
        foul_mod, shot_mod, stamina_mod, xg_mod = self.get_weather_modifiers()
        minute = self.match.current_minute

        team1_mid = self.match.team1.get_effective_midfield()
        team2_mid = self.match.team2.get_effective_midfield()
        total_mid = team1_mid + team2_mid
        if total_mid == 0:
            return
        prob_team1 = team1_mid / total_mid

        # Momentum bias (±5%)
        momentum_bias = (self.match.momentum1 - 50) / 1000.0
        prob_team1 = max(0.1, min(0.9, prob_team1 + momentum_bias))

        if random.random() < prob_team1:
            possessing_team = self.match.team1
            opposing_team   = self.match.team2
            self.match.possession1 += 1
        else:
            possessing_team = self.match.team2
            opposing_team   = self.match.team1
            self.match.possession2 += 1

        stamina_multiplier = 1.0 if minute <= 65 else 1.35
        for player in self.match.team1.get_active_players() + self.match.team2.get_active_players():
            drain = (random.uniform(0.4, 1.2) + stamina_mod) * stamina_multiplier
            player.stamina = max(0, player.stamina - drain)
            if random.random() < 0.45:
                player.passes_completed += 1

        if random.random() < 0.04:
            if possessing_team == self.match.team1:
                self.match.offsides1 += 1
            else:
                self.match.offsides2 += 1

        self.check_auto_substitutions(self.match.team1)
        self.check_auto_substitutions(self.match.team2)

        if random.random() < 0.004:
            all_active = self.match.team1.get_active_players() + self.match.team2.get_active_players()
            if all_active:
                self.generate_injury(random.choice(all_active))

        foul_chance = 0.08 + random.uniform(-0.03, 0.03) + foul_mod
        if random.random() < foul_chance:
            self.generate_foul(possessing_team, opposing_team)

        if random.random() < 0.04:
            active = [p for p in possessing_team.get_active_players() if p.position in ("MF", "FW")]
            if active:
                dribbler = random.choices(active, weights=[p.rating for p in active])[0]
                dribbler.dribbles += 1
                if possessing_team == self.match.team1:
                    self.match.dribbles1 += 1
                else:
                    self.match.dribbles2 += 1
                self.match.add_event(random.choice(DRIBBLE_EVENTS).format(name=dribbler.name))

        # ── Key pass event ──
        if random.random() < 0.05:
            active = [p for p in possessing_team.get_active_players() if p.position in ("MF", "FW")]
            if active:
                passer = random.choices(active, weights=[p.rating for p in active])[0]
                passer.key_passes += 1
                if possessing_team == self.match.team1:
                    self.match.key_passes1 += 1
                else:
                    self.match.key_passes2 += 1
                self.match.add_event(random.choice(KEY_PASS_EVENTS).format(name=passer.name))

        # ── Defensive clearance event ──
        if random.random() < 0.03:
            def_active = [p for p in opposing_team.get_active_players() if p.position == "DF"]
            if def_active:
                defender = random.choice(def_active)
                defender.clearances += 1
                if opposing_team == self.match.team1:
                    self.match.clearances1 += 1
                else:
                    self.match.clearances2 += 1
                self.match.add_event(random.choice(CLEARANCE_EVENTS).format(name=defender.name))

        if random.random() < 0.055:
            active = possessing_team.get_active_players()
            non_gk = [p for p in active if p.position != "GK"]
            if non_gk:
                player = random.choices(non_gk, weights=[p.rating for p in non_gk])[0]
                self.match.add_event(random.choice(COMMENTARY_POOL).format(name=player.name))

        shot_chance = (
            0.10
            + (possessing_team.get_effective_attack() - opposing_team.get_effective_defense()) / 200
            + shot_mod
        )
        shot_chance = max(0.01, min(0.22, shot_chance))
        if random.random() < shot_chance:
            atk_advantage = possessing_team.get_effective_attack() - opposing_team.get_effective_defense()
            is_big_chance = random.random() < max(0.05, min(0.25, atk_advantage / 150))
            self.generate_shot(possessing_team, opposing_team,
                               is_big_chance=is_big_chance, xg_mod=xg_mod)

    def check_auto_substitutions(self, team: Team):
        if team.subs_made >= 5:
            return
        active = team.get_active_players()
        bench = [p for p in team.players if p not in active and not p.injured and not p.red_cards]
        for player in active:
            if team.subs_made >= 5:
                break
            if player.stamina < 22 and player.position != "GK" and bench:
                sub = bench.pop(0)
                sub.stamina = 80 + random.randint(0, 15)
                player.injured = True
                team.subs_made += 1
                event = f"🔄 SUB: {player.name} ➡️ {sub.name} ({team.name})"
                self.match.substitutions.append(event)
                self.match.add_event(event)

    def generate_shot(self, possessing_team: Team, opposing_team: Team,
                       is_big_chance: bool = False, xg_mod: float = 0.0):
        """Handle shot generation and goal probability."""
        base_goal_prob = (
            0.12
            + (possessing_team.get_effective_attack() - opposing_team.get_effective_defense()) / 450
            + random.uniform(-0.04, 0.04)
            + xg_mod
        )
        if is_big_chance:
            base_goal_prob += 0.18
        goal_prob = max(0.02, min(0.42, base_goal_prob))

        xg_value = round(max(0.01, min(1.0, goal_prob)), 3)
        if possessing_team == self.match.team1:
            self.match.xg1 += xg_value
            self.match.shots1 += 1
        else:
            self.match.xg2 += xg_value
            self.match.shots2 += 1

        if is_big_chance:
            if possessing_team == self.match.team1:
                self.match.big_chances1 += 1
            else:
                self.match.big_chances2 += 1

        eligible = [p for p in possessing_team.get_active_players() if p.position != "GK"]
        if not eligible:
            return

        shooter = random.choices(eligible, weights=[p.rating for p in eligible])[0]
        shooter.shots_taken += 1

        if is_big_chance:
            intro = random.choice(BIG_CHANCE_INTRO).format(name=shooter.name)
            self.match.add_event(intro)
        else:
            self.match.add_event(random.choice(SHOT_THEMES).format(name=shooter.name))

        if random.random() < goal_prob:
            if possessing_team == self.match.team1:
                self.match.shots_on_target1 += 1
            else:
                self.match.shots_on_target2 += 1

            # VAR Check (8% chance → 30% disallowed)
            if random.random() < 0.08:
                self.match.add_event(f"📺 VAR REVIEW — Checking the goal by {shooter.name}...")
                if random.random() < 0.30:
                    reason = random.choice([
                        "Offside detected!", "Foul in the build-up!", "Handball in the box!"
                    ])
                    var_msg = f"❌ VAR DECISION: Goal DISALLOWED! {reason}"
                    self.match.var_decisions.append(var_msg)
                    self.match.add_event(var_msg)
                    return
                else:
                    self.match.add_event("✅ VAR DECISION: Goal STANDS!")

            shooter.goals += 1
            if possessing_team == self.match.team1:
                self.match.score1 += 1
            else:
                self.match.score2 += 1

            assist_candidates = [p for p in eligible if p != shooter]
            assister_str = ""
            if assist_candidates and random.random() < 0.85:
                assister = random.choices(assist_candidates, weights=[p.rating for p in assist_candidates])[0]
                assister.assists += 1
                assister_str = f" (assist: {assister.name})"
                if possessing_team == self.match.team1:
                    self.match.assists1 += 1
                else:
                    self.match.assists2 += 1

            pool = BIG_CHANCE_GOAL if is_big_chance else GOAL_MESSAGES
            msg = random.choice(pool).format(name=shooter.name, assist=assister_str)
            self.match.add_event(msg)
            self.match.scorers_list.append((shooter.name, self.match.current_minute, possessing_team.name))
            self.match.shift_momentum(possessing_team, amount=12.0)

        else:
            on_target = random.random() < 0.42
            if on_target:
                if possessing_team == self.match.team1:
                    self.match.shots_on_target1 += 1
                else:
                    self.match.shots_on_target2 += 1

            miss_pool = BIG_CHANCE_MISS if is_big_chance else MISS_MESSAGES
            miss_msg = random.choice(miss_pool).format(name=shooter.name)
            event = miss_msg
            if random.random() < 0.32 and not is_big_chance:
                event += " Corner kick awarded."
                if possessing_team == self.match.team1:
                    self.match.corners1 += 1
                else:
                    self.match.corners2 += 1
            self.match.add_event(event)
            self.match.shift_momentum(opposing_team, amount=4.0)

    def generate_foul(self, possessing_team: Team, opposing_team: Team):
        if possessing_team == self.match.team1:
            self.match.fouls2 += 1
        else:
            self.match.fouls1 += 1

        eligible = opposing_team.get_active_players()
        if not eligible:
            return
        fowler = random.choice(eligible)
        fowler.tackles += 1

        foul_descriptions = [
            f"Whistle blows! {fowler.name} commits a rough challenge.",
            f"{fowler.name} clatters into the attack — foul given!",
            f"Cynical foul by {fowler.name} to stop the counter.",
            f"{fowler.name} brings down the attacker — dangerous position!",
            f"Late challenge from {fowler.name} — the referee is not impressed!",
            f"{fowler.name} clips the heels of the attacker — foul!",
        ]
        event = random.choice(foul_descriptions)

        card_roll = random.random()
        if card_roll < 0.18:
            fowler.yellow_cards += 1
            event += f" 🟨 Yellow card for {fowler.name}!"
            if fowler.yellow_cards == 2:
                fowler.red_cards = 1
                event += " 🟥 Second yellow — he's off!"
        elif card_roll < 0.03:
            fowler.red_cards = 1
            event += f" 🟥 STRAIGHT RED! {fowler.name} walks — terrible decision!"

        if random.random() < 0.06:
            self.match.add_event(event)
            self._generate_free_kick(possessing_team, opposing_team)
            return

        self.match.add_event(event)

    def _generate_free_kick(self, attacking_team: Team, defending_team: Team):
        eligible = [p for p in attacking_team.get_active_players() if p.position != "GK"]
        if not eligible:
            return
        taker = random.choices(eligible, weights=[p.rating for p in eligible])[0]
        if random.random() < 0.13:
            taker.goals += 1
            if attacking_team == self.match.team1:
                self.match.score1 += 1
                self.match.shots_on_target1 += 1
                self.match.xg1 += 0.08
            else:
                self.match.score2 += 1
                self.match.shots_on_target2 += 1
                self.match.xg2 += 0.08
            self.match.add_event(
                f"🎯 FREE KICK GOAL! {taker.name} curls it beautifully into the top corner!"
            )
            self.match.scorers_list.append((taker.name, self.match.current_minute, attacking_team.name))
            self.match.shift_momentum(attacking_team, 10.0)
        else:
            miss = random.choice([
                f"🎯 Free kick from {taker.name} — blocked by the wall!",
                f"🎯 {taker.name}'s free kick drifts just over the bar!",
                f"🎯 The wall deflects {taker.name}'s effort — corner kick!",
            ])
            self.match.add_event(miss)

    def generate_injury(self, player: Player):
        player.injured = True
        team = self.match.team1 if player in self.match.team1.players else self.match.team2
        team_name = team.name
        injury_types = [
            "hamstring strain", "knocked ankle", "head clash",
            "twisted knee", "muscle cramp", "calf injury", "groin strain"
        ]
        injury_type = random.choice(injury_types)
        self.match.add_event(f"🏥 INJURY! {player.name} ({team_name}) is down with a {injury_type}!")

        if team.subs_made < 5:
            active = team.get_active_players()
            bench = [p for p in team.players if p not in active and not p.injured and not p.red_cards and p != player]
            if bench:
                sub = bench[0]
                sub.stamina = 80 + random.randint(0, 15)
                team.subs_made += 1
                sub_event = f"🔄 INJURY SUB: {sub.name} replaces {player.name} ({team_name})"
                self.match.substitutions.append(sub_event)
                self.match.add_event(sub_event)

    def penalty_shootout(self):
        self.match.penalties = True
        self.match.add_event("😰 Full extra time — still level! PENALTY SHOOTOUT begins!")
        pens1 = 0
        pens2 = 0
        round_num = 1

        kickers1 = [p for p in self.match.team1.get_active_players() if p.position != "GK"]
        kickers2 = [p for p in self.match.team2.get_active_players() if p.position != "GK"]
        keeper1  = next((p for p in self.match.team1.players if p.position == "GK"), None)
        keeper2  = next((p for p in self.match.team2.players if p.position == "GK"), None)
        keeper1_name = keeper1.name if keeper1 else "the keeper"
        keeper2_name = keeper2.name if keeper2 else "the keeper"

        while True:
            kicker1 = kickers1[(round_num - 1) % len(kickers1)] if kickers1 else None
            kicker1_name = kicker1.name if kicker1 else "Unknown"
            prob1 = 0.75 + (self.match.team1.get_effective_attack() - self.match.team2.get_effective_defense()) / 1000
            prob1 = max(0.6, min(0.9, prob1))
            if random.random() < prob1:
                pens1 += 1
                if kicker1:
                    kicker1.goals += 1
                res1 = f"✅ {kicker1_name} scores!"
            else:
                res1 = f"❌ {kicker1_name} misses! {keeper2_name} saves!"
                if keeper2:
                    keeper2.career_clean_sheets += 0

            kicker2 = kickers2[(round_num - 1) % len(kickers2)] if kickers2 else None
            kicker2_name = kicker2.name if kicker2 else "Unknown"
            prob2 = 0.75 + (self.match.team2.get_effective_attack() - self.match.team1.get_effective_defense()) / 1000
            prob2 = max(0.6, min(0.9, prob2))
            if random.random() < prob2:
                pens2 += 1
                if kicker2:
                    kicker2.goals += 1
                res2 = f"✅ {kicker2_name} scores!"
            else:
                res2 = f"❌ {kicker2_name} misses! {keeper1_name} saves!"

            event = (
                f"🎯 Pen round {round_num}: "
                f"{self.match.team1.name} — {res1} | "
                f"{self.match.team2.name} — {res2}  ({pens1}-{pens2})"
            )
            self.match.add_event(event)

            if round_num >= 5 and pens1 != pens2:
                break
            if round_num > 5 and abs(pens1 - pens2) > 0:
                break
            round_num += 1

        self.match.pens_score1 = pens1
        self.match.pens_score2 = pens2
        winner = self.match.team1.name if pens1 > pens2 else self.match.team2.name
        self.match.add_event(f"🏆 {winner} win the penalty shootout! ({pens1}-{pens2})")