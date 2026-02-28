import customtkinter as ctk
import json
import os
from typing import List
from datetime import datetime
from models.team import Team
from ui.theme import (CARD_BG, ACCENT, ACCENT_DARK, TEXT_PRIMARY, get_font, TEXT_SECONDARY,
                      BORDER_COLOR, EMERALD, EMERALD_DARK, ELECTRIC_BLUE, PURPLE, DANGER,
                      CARD_HOVER, BACKGROUND, WARNING, NEON_CYAN, ORANGE, ROSE,
                      ROW_EVEN, ROW_ODD, SUCCESS, create_icon_image)


class Dashboard(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team],
                 on_quick_match=None, on_start_season=None, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.on_quick_match = on_quick_match
        self.on_start_season = on_start_season
        self.setup_ui()

    def setup_ui(self):
        self.stats = {}
        if os.path.exists("data/stats.json"):
            with open("data/stats.json", "r") as f:
                self.stats = json.load(f)

        match_data = []
        if os.path.exists("data/matches.json"):
            with open("data/matches.json", "r") as f:
                match_data = json.load(f).get("matches", [])

        total_m     = len(match_data)
        total_goals = sum(self.stats.get("scorers", {}).values())
        total_assists = sum(self.stats.get("assists", {}).values())
        total_cs    = sum(self.stats.get("clean_sheets", {}).values())
        wins        = sum(1 for m in match_data if m.get("score1", 0) > m.get("score2", 0))
        win_rate    = f"{round(wins / total_m * 100)}%" if total_m else "—"
        avg_goals   = f"{round(total_goals / total_m, 1)}" if total_m else "—"
        total_xg    = sum(m.get("xg1", 0) + m.get("xg2", 0) for m in match_data)
        avg_xg      = f"{round(total_xg / total_m / 2, 2)}" if total_m else "—"

        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 8))

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.pack(side="left")
        
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            from PIL import Image
            img = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(46, 46))
            ctk.CTkLabel(left_h, text="", image=logo_img).pack(side="left", padx=(0, 12))
            
        text_h = ctk.CTkFrame(left_h, fg_color="transparent")
        text_h.pack(side="left")

        ctk.CTkLabel(text_h, text="COMMAND CENTER", font=get_font(26, "bold"),
                     text_color=TEXT_PRIMARY).pack(anchor="w")
        ts = datetime.now().strftime("%A, %d %B %Y — %H:%M")
        ctk.CTkLabel(text_h, text=ts, font=get_font(11),
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        btn_color = TEXT_PRIMARY
        ctk.CTkButton(actions, text=" Refresh", font=get_font(11), fg_color="transparent",
                       image=create_icon_image("\ue627", size=14, color=btn_color),
                       border_width=1, border_color=BORDER_COLOR, width=90, height=32,
                       corner_radius=8, command=self.refresh).pack(side="left", padx=(0, 6))
        ctk.CTkButton(actions, text=" Quick Match", font=get_font(12, "bold"),
                       image=create_icon_image("\uea0b", size=16, color=btn_color),
                       fg_color=EMERALD, hover_color=EMERALD_DARK, width=130, height=36,
                       corner_radius=8,
                       command=self.on_quick_match if self.on_quick_match else lambda: None
                       ).pack(side="left", padx=4)
        ctk.CTkButton(actions, text=" New Season", font=get_font(12, "bold"),
                       image=create_icon_image("\ue878", size=16, color=btn_color),
                       fg_color=ELECTRIC_BLUE, hover_color="#2563EB", width=130, height=36,
                       corner_radius=8,
                       command=self.on_start_season if self.on_start_season else lambda: None
                       ).pack(side="left", padx=4)

        grid = ctk.CTkFrame(self, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=6)

        cards = [
            ("\uea30", "MATCHES",     str(total_m),         ACCENT),
            ("\uea2f", "GOALS",        str(total_goals),      EMERALD),
            ("\ue8e5", "AVG GOALS",    avg_goals,             ELECTRIC_BLUE),
            ("\ue1b3", "ASSISTS",      str(total_assists),    PURPLE),
            ("\ue9e0", "CLEAN SHEETS", str(total_cs),         WARNING),
            ("\ue26b", "WIN RATE",     win_rate,              NEON_CYAN),
            ("\uef3e", "AVG xG",       avg_xg,               ORANGE),
        ]
        for col, (icon, label, value, color) in enumerate(cards):
            self._stat_card(grid, icon, label, value, color, col)

        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=(6, 16))

        res_frame = ctk.CTkFrame(main, fg_color=CARD_BG, border_width=1,
                                  border_color=BORDER_COLOR, corner_radius=12)
        res_frame.pack(side="left", fill="both", expand=True, padx=(0, 8))

        res_hdr = ctk.CTkFrame(res_frame, fg_color="transparent")
        res_hdr.pack(fill="x", padx=18, pady=(14, 2))
        list_icon = create_icon_image("\ue0ee", size=18, color=TEXT_PRIMARY)
        ctk.CTkLabel(res_hdr, text=" Recent Results", image=list_icon, font=get_font(15, "bold")).pack(side="left")
        ctk.CTkLabel(res_hdr, text="Last 12 matches", font=get_font(10),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=10, pady=(3, 0))

        self.results_list = ctk.CTkScrollableFrame(res_frame, fg_color="transparent")
        self.results_list.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        self._load_recent_results(match_data)

        right = ctk.CTkFrame(main, fg_color="transparent", width=295)
        right.pack(side="right", fill="both", padx=(8, 0))
        right.pack_propagate(False)

        elo_frame = ctk.CTkFrame(right, fg_color=CARD_BG, border_width=1,
                                  border_color=BORDER_COLOR, corner_radius=12)
        elo_frame.pack(fill="x", pady=(0, 8))
        lead_icon = create_icon_image("\uf20c", size=16, color=TEXT_PRIMARY)
        ctk.CTkLabel(elo_frame, text=" ELO Power Rankings", image=lead_icon,
                     font=get_font(13, "bold")).pack(pady=(12, 4), padx=15, anchor="w")
        self._load_elo_rankings(elo_frame)

        def create_ranked_section(title, icon_code, key, accent, pady=0):
            sf = ctk.CTkFrame(right, fg_color=CARD_BG, border_width=1, border_color=BORDER_COLOR, corner_radius=12)
            sf.pack(fill="both", expand=True, pady=pady)
            sec_icon = create_icon_image(icon_code, size=16, color=TEXT_PRIMARY)
            ctk.CTkLabel(sf, text=f" {title}", image=sec_icon, font=get_font(13, "bold")).pack(pady=(12, 4), padx=15, anchor="w")
            cnt = ctk.CTkFrame(sf, fg_color="transparent")
            cnt.pack(fill="both", expand=True, padx=10, pady=(0, 10))
            self._load_ranked_list(cnt, key, accent)

        create_ranked_section("Top Scorers", "\uea2f", "scorers", EMERALD, pady=(0, 6))
        create_ranked_section("Top Assists", "\ue1b3", "assists", ELECTRIC_BLUE)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self.setup_ui()

    def _stat_card(self, master, icon, label, value, accent_color, col):
        card = ctk.CTkFrame(master, fg_color=CARD_BG, border_width=1,
                             border_color=BORDER_COLOR, height=88, corner_radius=12)
        card.grid(row=0, column=col, padx=3, sticky="nsew")
        card.grid_propagate(False)
        master.columnconfigure(col, weight=1)

        top = ctk.CTkFrame(card, fg_color=accent_color, height=3, corner_radius=0)
        top.pack(fill="x")

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True)
        img = create_icon_image(icon, size=24, color=accent_color)
        if img:
            ctk.CTkLabel(inner, text="", image=img).pack(pady=(2, 0))
        else:
            ctk.CTkLabel(inner, text=icon, font=get_font(16)).pack(pady=(2, 0))
        ctk.CTkLabel(inner, text=value, font=get_font(18, "bold"),
                     text_color=accent_color).pack()
        ctk.CTkLabel(inner, text=label, font=get_font(8, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 2))

        def on_enter(e):
            card.configure(fg_color=CARD_HOVER)
        def on_leave(e):
            card.configure(fg_color=CARD_BG)
        card.bind("<Enter>", on_enter)
        card.bind("<Leave>", on_leave)

    def _load_elo_rankings(self, parent):
        sorted_teams = sorted(self.teams, key=lambda t: t.elo, reverse=True)[:6]
        max_elo = sorted_teams[0].elo if sorted_teams else 1600
        min_elo = 1300

        medals = {1: "🥇", 2: "🥈", 3: "🥉"}

        for i, t in enumerate(sorted_teams, 1):
            row = ctk.CTkFrame(parent, fg_color="transparent")
            row.pack(fill="x", padx=12, pady=2)

            medal = medals.get(i, f"{i}.")
            rank_color = ACCENT if i == 1 else (TEXT_SECONDARY if i > 3 else "#C0C0C0")
            ctk.CTkLabel(row, text=medal, font=get_font(11, "bold"),
                         text_color=rank_color, width=26).pack(side="left")
            ctk.CTkLabel(row, text=t.name, font=get_font(10, "bold")).pack(side="left", padx=2)
            ctk.CTkLabel(row, text=str(t.elo), font=get_font(11, "bold"),
                         text_color=ACCENT).pack(side="right")

            bar_pct = max(0.0, (t.elo - min_elo) / max(1, max_elo - min_elo))
            bar = ctk.CTkProgressBar(row, width=52, height=5, progress_color=rank_color,
                                      fg_color="#1A1A2A", corner_radius=2)
            bar.set(bar_pct)
            bar.pack(side="right", padx=5)

        ctk.CTkFrame(parent, height=10, fg_color="transparent").pack()

    def _load_recent_results(self, match_data):
        matches = match_data[-12:][::-1]
        if not matches:
            ctk.CTkLabel(self.results_list, text="No matches played yet",
                         font=get_font(13), text_color=TEXT_SECONDARY).pack(pady=50)
            return

        for i, m in enumerate(matches):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            row = ctk.CTkFrame(self.results_list, fg_color=bg, height=44, corner_radius=6)
            row.pack(fill="x", pady=1, padx=2)
            row.pack_propagate(False)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True)

            weather_icon = m.get("weather", "").split(" ")[0]
            if weather_icon:
                ctk.CTkLabel(inner, text=weather_icon, font=get_font(11), width=22).pack(side="left")

            ctk.CTkLabel(inner, text=m["team1"], font=get_font(11, "bold"),
                         width=130, anchor="e").pack(side="left")

            s1, s2 = m["score1"], m["score2"]
            if s1 > s2:
                score_color = EMERALD
            elif s1 < s2:
                score_color = DANGER
            else:
                score_color = TEXT_SECONDARY

            ctk.CTkLabel(inner, text=f"  {s1} – {s2}  ", font=get_font(14, "bold"),
                         text_color=score_color).pack(side="left")
            ctk.CTkLabel(inner, text=m["team2"], font=get_font(11, "bold"),
                         width=130, anchor="w").pack(side="left")

            xg1 = m.get("xg1", 0)
            xg2 = m.get("xg2", 0)
            if xg1 or xg2:
                ctk.CTkLabel(inner, text=f"xG {xg1:.1f}-{xg2:.1f}", font=get_font(8),
                             text_color=TEXT_SECONDARY, width=75).pack(side="right")

            motm = m.get("motm", "")
            if motm:
                ctk.CTkLabel(inner, text=f"⭐ {motm[:13]}", font=get_font(9),
                             text_color=ACCENT, width=100).pack(side="right")

    def _load_ranked_list(self, container, key, accent):
        data_dict = self.stats.get(key, {})
        items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)[:8]
        if not items:
            ctk.CTkLabel(container, text="No data yet", font=get_font(11),
                         text_color=TEXT_SECONDARY).pack(pady=15)
            return

        for i, (name, val) in enumerate(items):
            row = ctk.CTkFrame(container, fg_color="transparent")
            row.pack(fill="x", pady=1)
            rank_color = ACCENT if i == 0 else TEXT_SECONDARY
            ctk.CTkLabel(row, text=f"{i+1}.", font=get_font(10, "bold"),
                         text_color=rank_color, width=22).pack(side="left")
            ctk.CTkLabel(row, text=name, font=get_font(10)).pack(side="left", padx=3)
            ctk.CTkLabel(row, text=str(val), font=get_font(11, "bold"),
                         text_color=accent).pack(side="right")
