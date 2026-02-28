import customtkinter as ctk
from typing import List
from models.team import Team
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, TEXT_SECONDARY, BORDER_COLOR,
                      EMERALD, DANGER, ELECTRIC_BLUE, PURPLE, WARNING,
                      ROW_EVEN, ROW_ODD)


class PlayerRankings(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.current_filter = "ALL"
        self.current_sort = "rating"
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=25, pady=(20, 8))

        total_players = sum(len(t.players) for t in self.teams)
        ctk.CTkLabel(header, text="⭐ Player Rankings", font=get_font(24, "bold")).pack(side="left")
        ctk.CTkLabel(header, text=f"{total_players} players across {len(self.teams)} teams",
                     font=get_font(11), text_color=TEXT_SECONDARY).pack(side="left", padx=20, pady=(6, 0))

        # Filter + sort bar
        filter_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=10, height=46,
                                     border_width=1, border_color=BORDER_COLOR)
        filter_frame.pack(fill="x", padx=25, pady=(0, 8))
        filter_frame.pack_propagate(False)

        inner_filter = ctk.CTkFrame(filter_frame, fg_color="transparent")
        inner_filter.pack(expand=True)

        ctk.CTkLabel(inner_filter, text="Position:", font=get_font(11, "bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(12, 6))

        self.filter_buttons = {}
        positions = [("ALL", TEXT_PRIMARY), ("GK", WARNING), ("DF", EMERALD),
                     ("MF", ELECTRIC_BLUE), ("FW", DANGER)]
        for pos, color in positions:
            btn = ctk.CTkButton(
                inner_filter, text=pos, width=52, height=28, corner_radius=6,
                fg_color=ACCENT if pos == "ALL" else "transparent",
                text_color=TEXT_PRIMARY if pos == "ALL" else color,
                border_width=1, border_color=BORDER_COLOR, font=get_font(10, "bold"),
                command=lambda p=pos: self.set_filter(p)
            )
            btn.pack(side="left", padx=3)
            self.filter_buttons[pos] = btn

        ctk.CTkLabel(inner_filter, text="  Sort:", font=get_font(11, "bold"),
                     text_color=TEXT_SECONDARY).pack(side="left", padx=(12, 6))

        self.sort_buttons = {}
        sorts = [
            ("rating",    "Rating",     ACCENT),
            ("potential", "Potential",  PURPLE),
            ("age",       "Age",        TEXT_SECONDARY),
        ]
        for key, label, color in sorts:
            btn = ctk.CTkButton(
                inner_filter, text=label, width=72, height=28, corner_radius=6,
                fg_color=color if key == "rating" else "transparent",
                text_color=TEXT_PRIMARY if key == "rating" else TEXT_SECONDARY,
                border_width=1, border_color=BORDER_COLOR, font=get_font(10, "bold"),
                command=lambda k=key: self.set_sort(k)
            )
            btn.pack(side="left", padx=3)
            self.sort_buttons[key] = btn

        # Column header bar
        col_hdr = ctk.CTkFrame(self, fg_color="#0D0D16", height=30, corner_radius=0)
        col_hdr.pack(fill="x", padx=25, pady=(4, 0))
        col_hdr.pack_propagate(False)
        cols = [
            ("#",    35, "center"), ("Name", 180, "w"), ("Team", 140, "w"),
            ("POS",  46, "center"), ("Age",   42, "center"),
            ("OVR",  55, "center"), ("POT",   50, "center"),
            ("Form", 70, "center"),
        ]
        for txt, w, anchor in cols:
            ctk.CTkLabel(col_hdr, text=txt, font=get_font(9, "bold"), text_color=TEXT_SECONDARY,
                         width=w, anchor=anchor).pack(side="left")

        # Table
        self.table_frame = ctk.CTkFrame(self, fg_color=CARD_BG, corner_radius=12,
                                         border_width=1, border_color=BORDER_COLOR)
        self.table_frame.pack(fill="both", expand=True, padx=25, pady=(0, 15))

        self.render_table()

    # ────────────────────────────────────────────
    def set_filter(self, pos):
        self.current_filter = pos
        pos_colors = {"ALL": ACCENT, "GK": WARNING, "DF": EMERALD, "MF": ELECTRIC_BLUE, "FW": DANGER}
        for p, btn in self.filter_buttons.items():
            active = p == pos
            btn.configure(
                fg_color=pos_colors.get(p, ACCENT) if active else "transparent",
                text_color=TEXT_PRIMARY if active else pos_colors.get(p, TEXT_SECONDARY)
            )
        self.render_table()

    def set_sort(self, sort_key):
        self.current_sort = sort_key
        sort_colors = {"rating": ACCENT, "potential": PURPLE, "age": TEXT_SECONDARY}
        for k, btn in self.sort_buttons.items():
            active = k == sort_key
            btn.configure(
                fg_color=sort_colors.get(k, ACCENT) if active else "transparent",
                text_color=TEXT_PRIMARY if active else TEXT_SECONDARY
            )
        self.render_table()

    def render_table(self):
        for widget in self.table_frame.winfo_children():
            widget.destroy()

        # Collect + filter
        all_players = []
        for team in self.teams:
            for player in team.players:
                if self.current_filter == "ALL" or player.position == self.current_filter:
                    all_players.append((player, team.name))

        # Sort
        key_map = {
            "rating":    lambda x: x[0].rating,
            "potential": lambda x: x[0].potential,
            "age":       lambda x: x[0].age,
        }
        all_players.sort(key=key_map.get(self.current_sort, lambda x: x[0].rating), reverse=self.current_sort != "age")

        # Top-10 mini bar chart (only for rating sort)
        scroll = ctk.CTkScrollableFrame(self.table_frame, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=2)

        if all_players and self.current_sort == "rating":
            chart_frame = ctk.CTkFrame(scroll, fg_color="#0A0A14", corner_radius=8, height=100)
            chart_frame.pack(fill="x", padx=5, pady=(6, 10))
            chart_frame.pack_propagate(False)

            ctk.CTkLabel(chart_frame, text="Top 10 by Overall Rating",
                         font=get_font(10, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10, pady=(5, 0))

            bars_frame = ctk.CTkFrame(chart_frame, fg_color="transparent")
            bars_frame.pack(fill="both", expand=True, padx=10, pady=(0, 5))

            top10 = all_players[:10]
            max_r = max(p.rating for p, _ in top10) if top10 else 100

            for player, team_name in top10:
                col = ctk.CTkFrame(bars_frame, fg_color="transparent")
                col.pack(side="left", fill="y", expand=True, padx=1)

                bar_h = max(4, int((player.rating / max_r) * 48))
                ctk.CTkLabel(col, text=str(player.rating), font=get_font(7, "bold"), text_color=ACCENT).pack(side="bottom")
                ctk.CTkFrame(col, width=18, height=bar_h, fg_color=EMERALD, corner_radius=3).pack(side="bottom")
                ctk.CTkLabel(col, text=player.name.split()[-1][:6], font=get_font(6),
                             text_color=TEXT_SECONDARY).pack(side="bottom")

        # Rows
        pos_colors = {"GK": WARNING, "DF": EMERALD, "MF": ELECTRIC_BLUE, "FW": DANGER}

        for i, (player, team_name) in enumerate(all_players):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            row = ctk.CTkFrame(scroll, fg_color=bg, height=32, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            rank_color = ACCENT if i < 3 else TEXT_PRIMARY
            ctk.CTkLabel(row, text=str(i + 1), width=35, font=get_font(10, "bold"),
                         text_color=rank_color).pack(side="left")
            ctk.CTkLabel(row, text=player.name, width=180, anchor="w",
                         font=get_font(11, "bold" if i < 3 else "normal")).pack(side="left")
            ctk.CTkLabel(row, text=team_name, width=140, anchor="w", font=get_font(10),
                         text_color=TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(row, text=player.position, width=46, font=get_font(10, "bold"),
                         text_color=pos_colors.get(player.position, TEXT_PRIMARY)).pack(side="left")
            ctk.CTkLabel(row, text=str(player.age), width=42, font=get_font(10)).pack(side="left")

            # OVR badge coloring
            if player.rating >= 88:
                r_color = ACCENT
            elif player.rating >= 83:
                r_color = "#C0C0C0"
            else:
                r_color = "#CD7F32"
            ctk.CTkLabel(row, text=str(player.rating), width=55, font=get_font(12, "bold"),
                         text_color=r_color).pack(side="left")

            # Potential
            pot_diff = player.potential - player.rating
            pot_color = ELECTRIC_BLUE if pot_diff >= 5 else (EMERALD if pot_diff >= 2 else TEXT_SECONDARY)
            ctk.CTkLabel(row, text=str(player.potential), width=50, font=get_font(10),
                         text_color=pot_color).pack(side="left")

            # Form
            form_pct = min(1.0, player.form)
            form_color = EMERALD if form_pct >= 1.0 else (WARNING if form_pct >= 0.85 else DANGER)
            ctk.CTkLabel(row, text=f"{form_pct:.2f}", width=70, font=get_font(10, "bold"),
                         text_color=form_color).pack(side="left")
