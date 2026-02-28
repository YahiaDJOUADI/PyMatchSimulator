import customtkinter as ctk
import json
import os
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, TEXT_SECONDARY, BORDER_COLOR,
                      EMERALD, ELECTRIC_BLUE, PURPLE, DANGER, WARNING)


class AwardsView(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.stats_file = "data/stats.json"
        self.history_file = "data/matches.json"
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color=CARD_BG, height=84, corner_radius=12,
                               border_width=1, border_color=BORDER_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))

        h_inner = ctk.CTkFrame(header, fg_color="transparent")
        h_inner.pack(expand=True)

        ctk.CTkLabel(h_inner, text="🏆", font=get_font(30)).pack(side="left", padx=(0, 14))
        lbl_frame = ctk.CTkFrame(h_inner, fg_color="transparent")
        lbl_frame.pack(side="left")
        ctk.CTkLabel(lbl_frame, text="HALL OF FAME", font=get_font(22, "bold"),
                     text_color=ACCENT).pack(anchor="w")
        ctk.CTkLabel(lbl_frame, text="Career achievements, records & milestones",
                     font=get_font(11), text_color=TEXT_SECONDARY).pack(anchor="w")

        ctk.CTkButton(h_inner, text="🔄 Refresh", fg_color="transparent",
                       border_width=1, border_color=BORDER_COLOR, width=88, height=30,
                       corner_radius=6, font=get_font(11), command=self.refresh).pack(side="right", padx=(20, 0))

        self.content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=(0, 10))
        self.refresh()

    # ─────────────────────────────────────────────
    def refresh(self):
        for widget in self.content.winfo_children():
            widget.destroy()

        # ── Load data ──
        stats = {}
        if os.path.exists(self.stats_file):
            with open(self.stats_file, "r") as f:
                stats = json.load(f)

        match_data = []
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                match_data = json.load(f).get("matches", [])

        if not stats and not match_data:
            msg = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=12)
            msg.pack(fill="x", pady=40, padx=50)
            ctk.CTkLabel(msg, text="🎮 No career data yet.\nPlay some matches to start building records!",
                         font=get_font(14), text_color=TEXT_SECONDARY, justify="center").pack(pady=40)
            return

        # ── Summary bar ──
        total_goals   = sum(stats.get("scorers", {}).values())
        total_assists  = sum(stats.get("assists", {}).values())
        total_apps     = sum(stats.get("apps", {}).values())
        total_cs       = sum(stats.get("clean_sheets", {}).values())
        total_matches  = len(match_data)
        total_pens     = sum(1 for m in match_data if m.get("penalties"))

        summary = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=12,
                                border_width=1, border_color=BORDER_COLOR)
        summary.pack(fill="x", pady=(0, 12))

        s_row = ctk.CTkFrame(summary, fg_color="transparent")
        s_row.pack(pady=14)
        for val, label, color in [
            (str(total_matches),  "Matches",       ACCENT),
            (str(total_goals),    "Goals",         EMERALD),
            (str(total_assists),  "Assists",        ELECTRIC_BLUE),
            (str(total_cs),       "Clean Sheets",   PURPLE),
            (str(total_pens),     "Pen Shootouts",  WARNING),
        ]:
            sf = ctk.CTkFrame(s_row, fg_color="transparent")
            sf.pack(side="left", padx=22)
            ctk.CTkLabel(sf, text=val, font=get_font(26, "bold"), text_color=color).pack()
            ctk.CTkLabel(sf, text=label, font=get_font(9, "bold"), text_color=TEXT_SECONDARY).pack()

        # ── Match records ──
        if match_data:
            self._create_match_records(match_data)

        # ── Award sections ──
        sections = [
            ("⚽  GOLDEN BOOT",       "Top Scorers",         "scorers",      EMERALD),
            ("🎯  PLAYMAKER",         "Most Assists",         "assists",       ELECTRIC_BLUE),
            ("🧤  GOLDEN GLOVE",      "Clean Sheets",         "clean_sheets",  PURPLE),
            ("🏃  IRON MAN",          "Most Appearances",     "apps",          WARNING),
        ]
        for icon_label, subtitle, key, color in sections:
            self._create_award_section(icon_label, subtitle, stats.get(key, {}), color)

    def _create_match_records(self, match_data):
        """Show best/worst match stats as a mini record card."""
        high_scoring = max(match_data, key=lambda m: m["score1"] + m["score2"])
        total_hs = high_scoring["score1"] + high_scoring["score2"]

        records_card = ctk.CTkFrame(self.content, fg_color=CARD_BG, border_width=1,
                                     border_color=BORDER_COLOR, corner_radius=12)
        records_card.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(records_card, text="🔥  Match Records", font=get_font(14, "bold"),
                     text_color=ACCENT).pack(pady=(12, 6), padx=18, anchor="w")

        rec_row = ctk.CTkFrame(records_card, fg_color="transparent")
        rec_row.pack(fill="x", padx=16, pady=(0, 12))

        # Highest-scoring game
        r1 = ctk.CTkFrame(rec_row, fg_color="#10101A", corner_radius=8)
        r1.pack(side="left", expand=True, fill="x", padx=(0, 6))
        ctk.CTkLabel(r1, text="🏟️ Highest Scoring", font=get_font(10, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(8, 2))
        ctk.CTkLabel(r1, text=f"{high_scoring['team1']}  {high_scoring['score1']} – {high_scoring['score2']}  {high_scoring['team2']}",
                     font=get_font(11, "bold"), text_color=EMERALD, wraplength=220).pack(pady=(0, 4))
        ctk.CTkLabel(r1, text=f"{total_hs} goals total", font=get_font(9),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 8))

        # Total matches played
        r2 = ctk.CTkFrame(rec_row, fg_color="#10101A", corner_radius=8)
        r2.pack(side="right", expand=True, fill="x", padx=(6, 0))
        pen_matches = [m for m in match_data if m.get("penalties")]
        ctk.CTkLabel(r2, text="🎯 Penalty Shootouts", font=get_font(10, "bold"),
                     text_color=TEXT_SECONDARY).pack(pady=(8, 2))
        ctk.CTkLabel(r2, text=f"{len(pen_matches)} of {len(match_data)}",
                     font=get_font(18, "bold"), text_color=WARNING).pack(pady=(0, 2))
        pct = round(len(pen_matches) / len(match_data) * 100) if match_data else 0
        ctk.CTkLabel(r2, text=f"{pct}% of matches", font=get_font(9),
                     text_color=TEXT_SECONDARY).pack(pady=(0, 8))

    def _create_award_section(self, icon_title, subtitle, data, accent_color):
        if not data:
            return

        frame = ctk.CTkFrame(self.content, fg_color=CARD_BG, border_width=1,
                              border_color=BORDER_COLOR, corner_radius=12)
        frame.pack(fill="x", pady=5)

        # Section header
        hdr = ctk.CTkFrame(frame, fg_color="transparent")
        hdr.pack(fill="x", padx=18, pady=(12, 4))
        ctk.CTkLabel(hdr, text=icon_title, font=get_font(14, "bold"),
                     text_color=accent_color).pack(side="left")
        ctk.CTkLabel(hdr, text=subtitle, font=get_font(10),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=10, pady=(3, 0))

        sorted_data = sorted(data.items(), key=lambda x: x[1], reverse=True)[:8]

        for i, (name, val) in enumerate(sorted_data):
            bg = "#0F0F18" if i % 2 == 0 else "#14141E"
            row = ctk.CTkFrame(frame, fg_color=bg, height=32, corner_radius=0)
            row.pack(fill="x", padx=8, pady=0)
            row.pack_propagate(False)

            inner = ctk.CTkFrame(row, fg_color="transparent")
            inner.pack(expand=True, fill="x", padx=10)

            # Rank icon
            if i == 0:
                rank_txt, rank_color = "🥇", ACCENT
            elif i == 1:
                rank_txt, rank_color = "🥈", "#C0C0C0"
            elif i == 2:
                rank_txt, rank_color = "🥉", "#CD7F32"
            else:
                rank_txt, rank_color = f"{i+1}.", TEXT_SECONDARY

            ctk.CTkLabel(inner, text=rank_txt, font=get_font(11), width=30,
                         text_color=rank_color).pack(side="left")
            ctk.CTkLabel(inner, text=name,
                         font=get_font(11, "bold" if i < 3 else "normal")).pack(side="left", padx=4)

            # Value bar
            max_val = sorted_data[0][1] if sorted_data else 1
            bar_pct = val / max_val if max_val else 0
            bar = ctk.CTkProgressBar(inner, width=110, height=5,
                                      progress_color=accent_color, fg_color="#1A1A2A")
            bar.set(bar_pct)
            bar.pack(side="right", padx=(0, 8))
            ctk.CTkLabel(inner, text=str(val), font=get_font(12, "bold"),
                         text_color=accent_color, width=30).pack(side="right")

        ctk.CTkFrame(frame, height=6, fg_color="transparent").pack()
