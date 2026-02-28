import json
import os
import random
import customtkinter as ctk
from PIL import Image
from typing import List
from models.team import Team
from models.match import Match
from engine.simulator import SimulatorEngine
from ui.theme import (CARD_BG, ACCENT, ACCENT_DARK, TEXT_PRIMARY, get_font, SUCCESS, DANGER,
                      BORDER_COLOR, TEXT_SECONDARY, EMERALD, EMERALD_DARK, ELECTRIC_BLUE,
                      PURPLE, WARNING, BACKGROUND, CARD_HOVER, NEON_CYAN, ORANGE, ROSE)
from ui.components.tactics import TacticsBoard
from ui.components.pitch import PitchCanvas

# Speed settings: event display delay in ms
SPEED_SETTINGS = {"Slow": 380, "Normal": 160, "Fast": 45}

class MatchSimulator(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams      = teams
        self.team_names = [t.name for t in teams]

        self.simulation_index = 0
        self.match   = None
        self.engine  = None
        self.paused  = False
        self.speed   = "Normal"
        self.history_file   = "data/matches.json"
        self._halftime_shown = False

        self.setup_ui()

    def get_team_badge(self, team: Team, size=(40, 40)):
        if os.path.exists(team.logo_path):
            img = Image.open(team.logo_path)
            return ctk.CTkImage(light_image=img, dark_image=img, size=size)
        return None

    def setup_ui(self):
        self.selection_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.selection_frame.pack(fill="both", expand=True, pady=20, padx=20)

        center_card = ctk.CTkFrame(self.selection_frame, fg_color=CARD_BG,
                                    border_width=1, border_color=BORDER_COLOR, corner_radius=18)
        center_card.place(relx=0.5, rely=0.44, anchor="center")

        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(64, 64))
            ctk.CTkLabel(center_card, text="", image=logo_img).pack(pady=(24, 0))
        else:
            ctk.CTkLabel(center_card, text="⚡", font=get_font(48)).pack(pady=(28, 4))
            
        ctk.CTkLabel(center_card, text="NEW MATCH", font=get_font(24, "bold")).pack()
        ctk.CTkLabel(center_card, text="Select two teams and simulation speed",
                     font=get_font(12), text_color=TEXT_SECONDARY).pack(pady=(2, 16))

        selection = ctk.CTkFrame(center_card, fg_color="transparent")
        selection.pack(pady=4, padx=44)

        fa = ctk.CTkFrame(selection, fg_color="transparent")
        fa.grid(row=0, column=0, padx=16)
        ctk.CTkLabel(fa, text="HOME", font=get_font(10, "bold"), text_color=EMERALD).pack()
        self.team_a_var = ctk.StringVar(value=self.team_names[0])
        ctk.CTkComboBox(fa, values=self.team_names, variable=self.team_a_var,
                         width=190, height=34).pack(pady=6)

        ctk.CTkLabel(selection, text="VS", font=get_font(22, "bold"),
                     text_color=ACCENT).grid(row=0, column=1, padx=12)

        fb = ctk.CTkFrame(selection, fg_color="transparent")
        fb.grid(row=0, column=2, padx=16)
        ctk.CTkLabel(fb, text="AWAY", font=get_font(10, "bold"), text_color=DANGER).pack()
        self.team_b_var = ctk.StringVar(
            value=self.team_names[1] if len(self.team_names) > 1 else self.team_names[0]
        )
        ctk.CTkComboBox(fb, values=self.team_names, variable=self.team_b_var,
                         width=190, height=34).pack(pady=6)

        self.prob_frame = ctk.CTkFrame(center_card, fg_color="transparent")
        self.prob_frame.pack(pady=(2, 4))
        self.prob_lbl = ctk.CTkLabel(self.prob_frame, text="", font=get_font(10),
                                      text_color=TEXT_SECONDARY)
        self.prob_lbl.pack()
        self.team_a_var.trace("w", self._update_probability)
        self.team_b_var.trace("w", self._update_probability)
        self._update_probability()

        speed_frame = ctk.CTkFrame(center_card, fg_color="transparent")
        speed_frame.pack(pady=(6, 2))
        ctk.CTkLabel(speed_frame, text="⚡ Speed:", font=get_font(11, "bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(0, 8))
        self._speed_btn_map: dict = {}
        for spd in ["Slow", "Normal", "Fast"]:
            is_default = (spd == "Normal")
            b = ctk.CTkButton(
                speed_frame, text=spd, width=70, height=28,
                fg_color=ACCENT if is_default else "transparent",
                border_width=1, border_color=BORDER_COLOR, corner_radius=6,
                font=get_font(10, "bold"), hover_color=CARD_HOVER,
                command=lambda s=spd: self._select_speed(s)
            )
            b.pack(side="left", padx=3)
            self._speed_btn_map[spd] = b

        ctk.CTkButton(center_card, text="🏟️  Start Match", command=self.start_match,
                       fg_color=ACCENT, hover_color=ACCENT_DARK, corner_radius=10,
                       font=get_font(14, "bold"), height=46, width=220).pack(pady=(14, 32))

        self.match_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12)

    def _update_probability(self, *args):
        t1 = next((t for t in self.teams if t.name == self.team_a_var.get()), None)
        t2 = next((t for t in self.teams if t.name == self.team_b_var.get()), None)
        if not t1 or not t2 or t1 == t2:
            self.prob_lbl.configure(text="")
            return
        elo_diff = t1.elo - t2.elo
        win_prob = round(1 / (1 + 10 ** (-elo_diff / 400)) * 100)
        draw_prob = round(max(15, 30 - abs(elo_diff) / 20))
        win_prob = max(5, min(90, win_prob - draw_prob // 2))
        lose_prob = 100 - win_prob - draw_prob
        self.prob_lbl.configure(
            text=f"Prediction: Home {win_prob}%  Draw {draw_prob}%  Away {lose_prob}%"
        )

    def _select_speed(self, spd: str):
        self.speed = spd
        for s, b in self._speed_btn_map.items():
            b.configure(fg_color=ACCENT if s == spd else "transparent")

    def start_match(self):
        t1_name = self.team_a_var.get()
        t2_name = self.team_b_var.get()
        if t1_name == t2_name:
            return

        team1 = next(t for t in self.teams if t.name == t1_name)
        team2 = next(t for t in self.teams if t.name == t2_name)

        self.match  = Match(team1, team2)
        self.engine = SimulatorEngine(self.match)
        self.engine.simulate_match()

        self.selection_frame.pack_forget()
        self.setup_match_ui()
        self.match_frame.pack(pady=8, padx=12, fill="both", expand=True)

        self.simulation_index = 0
        self._halftime_shown  = False
        self.update_live()

    def setup_match_ui(self):
        for w in self.match_frame.winfo_children():
            w.destroy()

        self.top_frame = ctk.CTkFrame(self.match_frame, fg_color="transparent")
        self.top_frame.pack(fill="x", padx=16, pady=(10, 2))

        weather_badge = ctk.CTkFrame(self.top_frame, fg_color="#14141E", corner_radius=8, height=26)
        weather_badge.pack()
        ctk.CTkLabel(weather_badge, text=f"  {self.match.weather}  ", font=get_font(11),
                     text_color=TEXT_SECONDARY).pack(padx=6, pady=2)

        score_row = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        score_row.pack(pady=(4, 0))

        t1_img = self.get_team_badge(self.match.team1, size=(36, 36))
        if t1_img:
            ctk.CTkLabel(score_row, text="", image=t1_img).pack(side="left", padx=(0, 4))
            
        self.t1_name_lbl = ctk.CTkLabel(score_row, text=self.match.team1.name,
                                         font=get_font(18, "bold"), width=180, anchor="e")
        self.t1_name_lbl.pack(side="left", padx=8)
        
        self.score_label = ctk.CTkLabel(score_row, text="0 – 0", font=get_font(40, "bold"),
                                         text_color=TEXT_PRIMARY, width=140)
        self.score_label.pack(side="left")
        
        self.t2_name_lbl = ctk.CTkLabel(score_row, text=self.match.team2.name,
                                         font=get_font(18, "bold"), width=180, anchor="w")
        self.t2_name_lbl.pack(side="left", padx=8)

        t2_img = self.get_team_badge(self.match.team2, size=(36, 36))
        if t2_img:
            ctk.CTkLabel(score_row, text="", image=t2_img).pack(side="left", padx=(4, 0))

        time_row = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        time_row.pack()
        self.minute_label = ctk.CTkLabel(time_row, text="0'", font=get_font(14, "bold"),
                                          text_color=ACCENT)
        self.minute_label.pack(side="left", padx=(0, 8))
        self.progress_bar = ctk.CTkProgressBar(time_row, width=480, height=6,
                                                progress_color=ACCENT, fg_color="#121220", corner_radius=3)
        self.progress_bar.set(0)
        self.progress_bar.pack(side="left")

        mom_row = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        mom_row.pack(pady=(2, 0))
        ctk.CTkLabel(mom_row, text=self.match.team1.name[:8], font=get_font(8),
                     text_color=EMERALD, width=70, anchor="e").pack(side="left")
        self.momentum_bar = ctk.CTkProgressBar(mom_row, width=320, height=8,
                                                progress_color=EMERALD, fg_color=DANGER,
                                                corner_radius=4)
        self.momentum_bar.set(0.5)
        self.momentum_bar.pack(side="left", padx=6)
        ctk.CTkLabel(mom_row, text=self.match.team2.name[:8], font=get_font(8),
                     text_color=DANGER, width=70, anchor="w").pack(side="left")
        ctk.CTkLabel(mom_row, text="momentum", font=get_font(7),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=4)

        ctrl = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        ctrl.pack(pady=2)

        self.pause_btn = ctk.CTkButton(ctrl, text="⏸ PAUSE", command=self.toggle_pause,
                                        width=90, height=28, fg_color="#202030",
                                        corner_radius=6, font=get_font(11, "bold"))
        self.pause_btn.pack(side="left", padx=4)

        for label, spd in [("🐢", "Slow"), ("▶", "Normal"), ("⚡", "Fast")]:
            ctk.CTkButton(ctrl, text=label, width=32, height=28,
                           fg_color=ACCENT if spd == self.speed else "#202030",
                           corner_radius=6, font=get_font(11),
                           command=lambda s=spd: self._set_match_speed(s)
                           ).pack(side="left", padx=2)

        ctk.CTkButton(ctrl, text=f"⚙ {self.match.team1.name[:8]}",
                       command=lambda: self.open_match_tactics(self.match.team1),
                       width=105, height=28, fg_color="transparent",
                       border_width=1, border_color=BORDER_COLOR, corner_radius=6,
                       font=get_font(10)).pack(side="left", padx=6)
        ctk.CTkButton(ctrl, text=f"⚙ {self.match.team2.name[:8]}",
                       command=lambda: self.open_match_tactics(self.match.team2),
                       width=105, height=28, fg_color="transparent",
                       border_width=1, border_color=BORDER_COLOR, corner_radius=6,
                       font=get_font(10)).pack(side="left", padx=2)

        self.main_split = ctk.CTkFrame(self.match_frame, fg_color="transparent")
        self.main_split.pack(fill="both", expand=True, padx=10, pady=4)

        self.left_panel = ctk.CTkFrame(self.main_split, fg_color="transparent")
        self.left_panel.pack(side="left", fill="both", expand=True)

        self.pitch_canvas = PitchCanvas(self.left_panel)
        self.pitch_canvas.pack(pady=(0, 3))

        stam_row = ctk.CTkFrame(self.left_panel, fg_color="transparent", height=18)
        stam_row.pack(fill="x", padx=6, pady=(0, 3))
        ctk.CTkLabel(stam_row, text=self.match.team1.name[:12], font=get_font(9),
                     width=90, anchor="e").pack(side="left")
        self.stamina_bar1 = ctk.CTkProgressBar(stam_row, width=130, height=8, progress_color=EMERALD,
                                                fg_color="#141428")
        self.stamina_bar1.set(1.0)
        self.stamina_bar1.pack(side="left", padx=4)
        ctk.CTkLabel(stam_row, text="FITNESS", font=get_font(8, "bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=8)
        self.stamina_bar2 = ctk.CTkProgressBar(stam_row, width=130, height=8, progress_color=EMERALD,
                                                fg_color="#141428")
        self.stamina_bar2.set(1.0)
        self.stamina_bar2.pack(side="left", padx=4)
        ctk.CTkLabel(stam_row, text=self.match.team2.name[:12], font=get_font(9),
                     width=90, anchor="w").pack(side="left")

        self.log_text = ctk.CTkTextbox(self.left_panel, fg_color="#07070F", border_width=1,
                                        border_color=BORDER_COLOR, font=get_font(11), corner_radius=8)
        self.log_text.pack(fill="both", expand=True, padx=2)
        self.log_text.tag_config("goal",     foreground=SUCCESS)
        self.log_text.tag_config("var",      foreground=WARNING)
        self.log_text.tag_config("sub",      foreground=ELECTRIC_BLUE)
        self.log_text.tag_config("card",     foreground=ORANGE)
        self.log_text.tag_config("injury",   foreground=DANGER)
        self.log_text.tag_config("halftime", foreground=ACCENT)
        self.log_text.tag_config("freekick", foreground=PURPLE)
        self.log_text.tag_config("dim",      foreground=TEXT_SECONDARY)
        self.log_text.tag_config("bigchance", foreground=ORANGE)
        self.log_text.tag_config("dribble",  foreground=NEON_CYAN)
        self.log_text.tag_config("keypas",   foreground="#A855F7")
        self.log_text.tag_config("defend",   foreground=EMERALD)

        self.stats_panel = ctk.CTkFrame(self.main_split, width=245, fg_color="#0B0B1A",
                                         border_width=1, border_color=BORDER_COLOR, corner_radius=10)
        self.stats_panel.pack(side="right", fill="both", padx=(8, 0))
        self.stats_panel.pack_propagate(False)

        hdr = ctk.CTkFrame(self.stats_panel, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(10, 2))
        ctk.CTkLabel(hdr, text=self.match.team1.name[:10], font=get_font(9, "bold"),
                     text_color=EMERALD, width=92, anchor="w").pack(side="left")
        ctk.CTkLabel(hdr, text="STAT", font=get_font(9, "bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", expand=True)
        ctk.CTkLabel(hdr, text=self.match.team2.name[:10], font=get_font(9, "bold"),
                     text_color=ELECTRIC_BLUE, width=92, anchor="e").pack(side="right")

        ctk.CTkFrame(self.stats_panel, height=1, fg_color=BORDER_COLOR).pack(fill="x", pady=4, padx=10)

        ctk.CTkLabel(self.stats_panel, text="⚽ SCORERS", font=get_font(10, "bold"),
                     text_color=ACCENT).pack(pady=(4, 2))
        self.scorers_text = ctk.CTkLabel(self.stats_panel, text="—", font=get_font(9),
                                          text_color=TEXT_SECONDARY, wraplength=220)
        self.scorers_text.pack(pady=2)

        ctk.CTkFrame(self.stats_panel, height=1, fg_color=BORDER_COLOR).pack(fill="x", pady=5, padx=12)

        self.inner_stats = ctk.CTkFrame(self.stats_panel, fg_color="transparent")
        self.inner_stats.pack(fill="both", expand=True, padx=6)

        self.stat_widgets = {}
        stats_def = [
            ("Possession", ACCENT),
            ("Shots",      TEXT_PRIMARY),
            ("On Target",  EMERALD),
            ("xG",         ORANGE),
            ("Big Chances",NEON_CYAN),
            ("Key Passes", PURPLE),
            ("Fouls",      "#FF8C00"),
            ("Corners",    ELECTRIC_BLUE),
            ("Offsides",   TEXT_SECONDARY),
            ("Yellow ⊕",   WARNING),
            ("Red ⊠",      DANGER),
        ]
        for i, (s, col) in enumerate(stats_def):
            lbl = ctk.CTkLabel(self.inner_stats, text=s, font=get_font(8, "bold"),
                                text_color=col)
            lbl.grid(row=i * 2, column=0, columnspan=3, pady=(3, 0), sticky="ew")
            p1 = ctk.CTkLabel(self.inner_stats, text="0", font=get_font(11, "bold"))
            p1.grid(row=i * 2 + 1, column=0, padx=4, sticky="e")
            sep = ctk.CTkLabel(self.inner_stats, text="—", font=get_font(9),
                                text_color=BORDER_COLOR)
            sep.grid(row=i * 2 + 1, column=1)
            p2 = ctk.CTkLabel(self.inner_stats, text="0", font=get_font(11, "bold"))
            p2.grid(row=i * 2 + 1, column=2, padx=4, sticky="w")
            self.stat_widgets[s] = (p1, p2)

        self.inner_stats.columnconfigure(0, weight=1)
        self.inner_stats.columnconfigure(1, weight=0)
        self.inner_stats.columnconfigure(2, weight=1)

    def _set_match_speed(self, spd: str):
        self.speed = spd

    def toggle_pause(self):
        self.paused = not self.paused
        self.pause_btn.configure(text="▶ RESUME" if self.paused else "⏸ PAUSE")

    def open_match_tactics(self, team: Team):
        if not self.paused:
            self.toggle_pause()
        board = TacticsBoard(
            self.match_frame, team,
            on_save=lambda: self.log_text.insert(
                "end", f"⚙️ TACTICAL CHANGE: {team.name} → {team.formation}\n", "sub"
            )
        )
        board.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.44, relheight=0.60)



    def update_live(self):
        if self.paused:
            self.after(400, self.update_live)
            return

        if self.simulation_index < len(self.match.events):
            event = self.match.events[self.simulation_index]

            if "HALF TIME" in event and not self._halftime_shown:
                self._halftime_shown = True
                self._show_halftime_popup()

            self._write_event(event)
            self.log_text.see("end")
            self.simulation_index += 1

            self.pitch_canvas.animate_ball(event)

            min_str = event.split("'")[0].strip()
            if min_str.isdigit():
                m = int(min_str)
                suffix = "'" if m <= 90 else " ET'"
                self.minute_label.configure(text=f"{min_str}{suffix}")
                self.progress_bar.set(min(1.0, m / 90.0))

                a1 = self.match.team1.get_active_players()
                a2 = self.match.team2.get_active_players()
                avg1 = sum(p.stamina for p in a1) / max(1, len(a1)) / 100.0
                avg2 = sum(p.stamina for p in a2) / max(1, len(a2)) / 100.0
                self.stamina_bar1.set(max(0, avg1))
                self.stamina_bar2.set(max(0, avg2))
                for bar, val in [(self.stamina_bar1, avg1), (self.stamina_bar2, avg2)]:
                    bar.configure(progress_color=(
                        DANGER if val < 0.3 else (WARNING if val < 0.6 else EMERALD)
                    ))

                mom1 = self.match.momentum1 / 100.0
                self.momentum_bar.set(max(0.0, min(1.0, mom1)))

            if "GOAL" in event.upper() and "DISALLOWED" not in event.upper():
                self.score_label.configure(text=f"{self.match.score1} – {self.match.score2}")
                self.flash_score()
                self.update_scorers(event)

            self.update_stats()
            delay = SPEED_SETTINGS.get(self.speed, 160)
            self.after(delay, self.update_live)
        else:
            self.finish_match()

    def _write_event(self, event: str):
        ev = event.upper()
        tag = None
        if "GOAL" in ev and "DISALLOWED" not in ev:
            tag = "goal"
        elif "VAR" in ev or "DISALLOWED" in ev:
            tag = "var"
        elif "SUB" in ev or "SUBSTITUT" in ev:
            tag = "sub"
        elif "🟨" in event or "🟥" in event:
            tag = "card"
        elif "🏥" in event or "INJURY" in ev:
            tag = "injury"
        elif "HALF TIME" in ev:
            tag = "halftime"
        elif "FREE KICK" in ev:
            tag = "freekick"
        elif "BIG CHANCE" in ev or "HUGE OPPORTUNITY" in ev or "GILT-EDGED" in ev:
            tag = "bigchance"
        elif "🌀" in event:
            tag = "dribble"
        elif "🔑" in event:
            tag = "keypas"
        elif "🛡️" in event:
            tag = "defend"
        elif any(k in event for k in ["drives forward", "clever", "Beautiful", "Pressing",
                                       "ghosting", "turns sharply", "demands"]):
            tag = "dim"

        if tag:
            self.log_text.insert("end", event + "\n", tag)
        else:
            self.log_text.insert("end", event + "\n")



    def update_stats(self):
        total = self.match.possession1 + self.match.possession2
        p1 = round(self.match.possession1 / total * 100) if total > 0 else 50
        p2 = 100 - p1

        vals = {
            "Possession":  (f"{p1}%", f"{p2}%"),
            "Shots":       (str(self.match.shots1),           str(self.match.shots2)),
            "On Target":   (str(self.match.shots_on_target1), str(self.match.shots_on_target2)),
            "xG":          (f"{self.match.xg1:.1f}",          f"{self.match.xg2:.1f}"),
            "Big Chances": (str(self.match.big_chances1),     str(self.match.big_chances2)),
            "Key Passes":  (str(self.match.key_passes1),      str(self.match.key_passes2)),
            "Fouls":       (str(self.match.fouls1),           str(self.match.fouls2)),
            "Corners":     (str(self.match.corners1),         str(self.match.corners2)),
            "Offsides":    (str(self.match.offsides1),        str(self.match.offsides2)),
            "Yellow ⊕":   (str(self.match.get_yellow_cards(self.match.team1)),
                            str(self.match.get_yellow_cards(self.match.team2))),
            "Red ⊠":      (str(self.match.get_red_cards(self.match.team1)),
                            str(self.match.get_red_cards(self.match.team2))),
        }
        for key, (v1, v2) in vals.items():
            if key in self.stat_widgets:
                self.stat_widgets[key][0].configure(text=v1)
                self.stat_widgets[key][1].configure(text=v2)

    def flash_score(self):
        self.score_label.configure(text_color=SUCCESS)
        self.after(800, lambda: self.score_label.configure(text_color=TEXT_PRIMARY))

    def update_scorers(self, event: str):
        current = self.scorers_text.cget("text")
        if current == "—":
            current = ""
        try:
            min_str = event.split("'")[0].strip()
            if "GOAL" in event.upper():
                after = event.split("!")
                if len(after) > 1:
                    part = after[1].strip()
                    for stopper in ["ripples", "makes", "header", "capitalizes", "What",
                                    "Pure", "tap-in", "buries", "Unstoppable", "punishes",
                                    "composed", "converted", "bends", "rocket"]:
                        part = part.split(stopper)[0]
                    scorer_clean = part.split("(assist")[0].strip()
                    if scorer_clean:
                        new_entry = f"{scorer_clean} ({min_str}')"
                        if new_entry not in current:
                            self.scorers_text.configure(text=(current + "\n" + new_entry).strip())
        except Exception:
            pass

    def _show_halftime_popup(self):
        self.paused = True
        self.pause_btn.configure(text="▶ RESUME")

        popup = ctk.CTkFrame(self.match_frame, fg_color="#0A0A18", border_width=2,
                              border_color=ACCENT, corner_radius=16)
        popup.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.50, relheight=0.56)

        ctk.CTkLabel(popup, text="🔔  HALF TIME", font=get_font(20, "bold"),
                     text_color=ACCENT).pack(pady=(16, 4))
        ctk.CTkLabel(popup,
                     text=f"{self.match.team1.name}  {self.match.score1} — {self.match.score2}  {self.match.team2.name}",
                     font=get_font(17, "bold")).pack(pady=(0, 10))

        sg = ctk.CTkFrame(popup, fg_color="transparent")
        sg.pack(padx=28)

        total  = self.match.possession1 + self.match.possession2
        p1_pct = round(self.match.possession1 / total * 100) if total else 50

        ht_stats = [
            ("Possession",  f"{p1_pct}%",                         f"{100 - p1_pct}%"),
            ("Shots",       str(self.match.shots1),               str(self.match.shots2)),
            ("On Target",   str(self.match.shots_on_target1),     str(self.match.shots_on_target2)),
            ("xG",          f"{self.match.xg1:.1f}",              f"{self.match.xg2:.1f}"),
            ("Big Chances", str(self.match.big_chances1),          str(self.match.big_chances2)),
            ("Fouls",       str(self.match.fouls1),               str(self.match.fouls2)),
        ]
        for label, v1, v2 in ht_stats:
            row = ctk.CTkFrame(sg, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=v1, font=get_font(12, "bold"), text_color=EMERALD,
                         width=55, anchor="e").pack(side="left")
            ctk.CTkLabel(row, text=label, font=get_font(11), text_color=TEXT_SECONDARY,
                         width=100).pack(side="left", padx=8)
            ctk.CTkLabel(row, text=v2, font=get_font(12, "bold"), text_color=ELECTRIC_BLUE,
                         width=55, anchor="w").pack(side="left")

        def resume():
            popup.destroy()
            self.paused = False
            self.pause_btn.configure(text="⏸ PAUSE")

        ctk.CTkButton(popup, text="▶  Continue 2nd Half", command=resume,
                       fg_color=ACCENT, hover_color=ACCENT_DARK, corner_radius=8,
                       font=get_font(13, "bold"), height=38).pack(pady=(12, 16))

    def finish_match(self):
        self.minute_label.configure(text="FT", text_color=SUCCESS)
        self.progress_bar.set(1.0)
        self.save_history()
        self.show_post_match_report()

    def show_post_match_report(self):
        report = ctk.CTkFrame(self.match_frame, fg_color="#09091A", border_width=2,
                               border_color=ACCENT, corner_radius=16)
        report.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.60, relheight=0.88)

        ctk.CTkLabel(report, text="📊  POST-MATCH REPORT", font=get_font(18, "bold"),
                     text_color=ACCENT).pack(pady=(14, 2))
        ctk.CTkLabel(report,
                     text=f"{self.match.team1.name}  {self.match.score1} — {self.match.score2}  {self.match.team2.name}",
                     font=get_font(18, "bold")).pack()

        if self.match.penalties:
            ctk.CTkLabel(report,
                         text=f"(Penalties: {self.match.pens_score1} — {self.match.pens_score2})",
                         font=get_font(12), text_color=WARNING).pack()

        if self.match.man_of_match:
            motm_row = ctk.CTkFrame(report, fg_color="#141422", corner_radius=8)
            motm_row.pack(fill="x", padx=20, pady=6)
            ctk.CTkLabel(motm_row,
                         text=f"⭐  Man of the Match: {self.match.man_of_match.name}  —  {self.match.man_of_match.match_rating}/10",
                         font=get_font(13, "bold"), text_color=ACCENT).pack(pady=7)

        stat_row = ctk.CTkFrame(report, fg_color="#0C0C18", corner_radius=8)
        stat_row.pack(fill="x", padx=20, pady=(0, 4))
        total = self.match.possession1 + self.match.possession2
        p1 = round(self.match.possession1 / total * 100) if total else 50

        for label, v1, v2 in [
            ("Possession",  f"{p1}%",                         f"{100-p1}%"),
            ("Shots / Target", f"{self.match.shots1}/{self.match.shots_on_target1}",
                               f"{self.match.shots2}/{self.match.shots_on_target2}"),
            ("xG",          f"{self.match.xg1:.2f}",          f"{self.match.xg2:.2f}"),
            ("Big Chances", str(self.match.big_chances1),     str(self.match.big_chances2)),
            ("Key Passes",  str(self.match.key_passes1),      str(self.match.key_passes2)),
            ("Fouls",       str(self.match.fouls1),           str(self.match.fouls2)),
        ]:
            r = ctk.CTkFrame(stat_row, fg_color="transparent")
            r.pack(fill="x", padx=24, pady=1)
            ctk.CTkLabel(r, text=v1, font=get_font(11, "bold"), text_color=EMERALD,
                         width=60, anchor="e").pack(side="left")
            ctk.CTkLabel(r, text=label, font=get_font(10), text_color=TEXT_SECONDARY,
                         width=100).pack(side="left", padx=6)
            ctk.CTkLabel(r, text=v2, font=get_font(11, "bold"), text_color=ELECTRIC_BLUE,
                         width=60, anchor="w").pack(side="left")

        footer = ctk.CTkFrame(report, fg_color="transparent")
        footer.pack(side="bottom", fill="x", padx=20, pady=(4, 16))
        ctk.CTkButton(footer, text="🔄  New Match", command=self.reset_sim,
                       fg_color=ACCENT, hover_color=ACCENT_DARK, corner_radius=8,
                       font=get_font(13, "bold"), height=42).pack(fill="x")

        rat_frame = ctk.CTkScrollableFrame(report, fg_color="transparent", height=130)
        rat_frame.pack(fill="both", expand=True, padx=14, pady=(2, 4))

        cols_f = ctk.CTkFrame(rat_frame, fg_color="transparent")
        cols_f.pack(fill="x")

        for team, col_color, side in [
            (self.match.team1, EMERALD, "left"),
            (self.match.team2, ELECTRIC_BLUE, "right"),
        ]:
            col = ctk.CTkFrame(cols_f, fg_color="transparent")
            col.pack(side=side, fill="both", expand=True, padx=5)
            ctk.CTkLabel(col, text=team.name, font=get_font(11, "bold"),
                         text_color=col_color).pack(anchor="w")
            for p, rating in self.match.get_player_ratings(team):
                if rating >= 8:
                    r_color = ACCENT
                elif rating >= 7:
                    r_color = EMERALD
                elif rating >= 6:
                    r_color = TEXT_SECONDARY
                else:
                    r_color = DANGER
                rr = ctk.CTkFrame(col, fg_color="transparent")
                rr.pack(fill="x")
                ctk.CTkLabel(rr, text=f"#{p.number}", font=get_font(8),
                             text_color=TEXT_SECONDARY, width=26).pack(side="left")
                ctk.CTkLabel(rr, text=p.name, font=get_font(9), anchor="w").pack(side="left")
                ctk.CTkLabel(rr, text=str(rating), font=get_font(10, "bold"),
                             text_color=r_color).pack(side="right")


    def save_history(self):
        from utils.history_manager import save_match_history, update_career_stats
        save_match_history(self.match, self.history_file)
        update_career_stats(self.match)

        pass

    def reset_sim(self):
        self.match_frame.pack_forget()
        for w in self.match_frame.winfo_children():
            w.destroy()
        self.selection_frame.pack(fill="both", expand=True, pady=20, padx=20)
