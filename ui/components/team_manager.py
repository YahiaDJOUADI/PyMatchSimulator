import random
import customtkinter as ctk
from typing import List
from models.team import Team
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, TEXT_SECONDARY,
                      BORDER_COLOR, EMERALD, DANGER, ELECTRIC_BLUE, PURPLE,
                      WARNING, ROW_EVEN, ROW_ODD)
from ui.components.tactics import TacticsBoard


class TeamManager(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.selected_team = None
        self.active_tab = "squad"
        self.setup_ui()

    def setup_ui(self):
        self.list_frame = ctk.CTkFrame(self, fg_color=CARD_BG, width=235, border_width=1,
                                        border_color=BORDER_COLOR, corner_radius=12)
        self.list_frame.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.list_frame.pack_propagate(False)

        ctk.CTkLabel(self.list_frame, text="👥  SQUADS", font=get_font(16, "bold"),
                     text_color=ACCENT).pack(pady=(15, 2))
        ctk.CTkLabel(self.list_frame, text=f"{len(self.teams)} teams available",
                     font=get_font(10), text_color=TEXT_SECONDARY).pack(pady=(0, 10))

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self._filter_list)
        search = ctk.CTkEntry(self.list_frame, textvariable=self.search_var,
                               placeholder_text="🔍  Search team…", height=30,
                               fg_color="#0D0D18", border_color=BORDER_COLOR, corner_radius=8)
        search.pack(fill="x", padx=10, pady=(0, 8))

        self.scroll_list = ctk.CTkScrollableFrame(self.list_frame, fg_color="transparent")
        self.scroll_list.pack(fill="both", expand=True, padx=5)
        self._render_list()

        self.details_frame = ctk.CTkFrame(self, fg_color=CARD_BG, border_width=1,
                                           border_color=BORDER_COLOR, corner_radius=12)
        self.details_frame.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

        self.no_selection_label = ctk.CTkLabel(
            self.details_frame, text="← Select a team to view details",
            font=get_font(16), text_color=TEXT_SECONDARY
        )
        self.no_selection_label.pack(expand=True)

    def _render_list(self, query=""):
        for w in self.scroll_list.winfo_children():
            w.destroy()
        for team in self.teams:
            if query and query.lower() not in team.name.lower():
                continue
            btn = ctk.CTkButton(
                self.scroll_list, text=f"  {team.name}",
                command=lambda t=team: self.show_team_details(t),
                fg_color="transparent", hover_color="#1A1A28",
                anchor="w", font=get_font(13), height=38, corner_radius=8
            )
            btn.pack(fill="x", pady=2)

    def _filter_list(self, *args):
        self._render_list(self.search_var.get())

    def show_team_details(self, team: Team):
        self.selected_team = team
        self.active_tab = "squad"
        self._render_details()

    def _render_details(self):
        team = self.selected_team
        if not team:
            return
        for widget in self.details_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        header.pack(fill="x", pady=(18, 8), padx=20)

        ctk.CTkLabel(header, text=team.name, font=get_font(26, "bold")).pack(side="left")

        badges = ctk.CTkFrame(header, fg_color="transparent")
        badges.pack(side="right")
        for txt, color in [(f"ELO {team.elo}", ACCENT), (team.formation, PURPLE)]:
            b = ctk.CTkFrame(badges, fg_color="#1A1A28", corner_radius=8)
            b.pack(side="left", padx=4)
            ctk.CTkLabel(b, text=f"  {txt}  ", font=get_font(11, "bold"),
                         text_color=color).pack(padx=4, pady=3)

        stats_frame = ctk.CTkFrame(self.details_frame, fg_color="#0D0D16", corner_radius=10)
        stats_frame.pack(fill="x", padx=20, pady=4)
        stat_items = [
            ("Attack",  team.attack,                    DANGER),
            ("Midfield", team.midfield,                 ELECTRIC_BLUE),
            ("Defense", team.defense,                   EMERALD),
            ("Overall", round(team.overall_rating),     ACCENT),
        ]
        for i, (label, val, color) in enumerate(stat_items):
            sf = ctk.CTkFrame(stats_frame, fg_color="transparent")
            sf.grid(row=0, column=i, padx=20, pady=10)
            ctk.CTkLabel(sf, text=str(val), font=get_font(22, "bold"), text_color=color).pack()
            ctk.CTkLabel(sf, text=label, font=get_font(9, "bold"), text_color=TEXT_SECONDARY).pack()
        stats_frame.columnconfigure((0, 1, 2, 3), weight=1)

        mc_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        mc_frame.pack(fill="x", padx=20, pady=4)
        for label, val, max_val, color, extra in [
            ("Morale",    team.morale,    1.5, EMERALD if team.morale >= 1.0 else DANGER, team.get_morale_label()),
            ("Chemistry", team.chemistry, 1.2, ELECTRIC_BLUE, f"{team.chemistry:.2f}"),
        ]:
            box = ctk.CTkFrame(mc_frame, fg_color="#0D0D16", corner_radius=8)
            box.pack(side="left", fill="x", expand=True, padx=(0, 4) if label == "Morale" else (4, 0))
            row = ctk.CTkFrame(box, fg_color="transparent")
            row.pack(padx=14, pady=8)
            ctk.CTkLabel(row, text=label, font=get_font(10, "bold"), text_color=TEXT_SECONDARY,
                         width=60).pack(side="left")
            bar = ctk.CTkProgressBar(row, width=90, height=7, progress_color=color, fg_color="#121220")
            bar.set(min(1.0, val / max_val))
            bar.pack(side="left", padx=8)
            ctk.CTkLabel(row, text=extra, font=get_font(10, "bold"), text_color=color).pack(side="left")

        tab_frame = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        tab_frame.pack(fill="x", padx=20, pady=(6, 0))
        for key, label in [("squad", "🧑 Squad"), ("career", "📊 Career Stats"), ("tactics", "⚙️ Tactics")]:
            active = self.active_tab == key
            btn = ctk.CTkButton(
                tab_frame, text=label, height=30, width=120,
                fg_color=ACCENT if active else "transparent",
                border_width=1, border_color=ACCENT if active else BORDER_COLOR,
                corner_radius=6, font=get_font(11, "bold" if active else "normal"),
                command=lambda k=key: self._switch_tab(k)
            )
            btn.pack(side="left", padx=(0, 6))

        self.tab_content = ctk.CTkFrame(self.details_frame, fg_color="transparent")
        self.tab_content.pack(fill="both", expand=True, padx=12, pady=6)

        if self.active_tab == "squad":
            self._render_squad_tab(team)
        elif self.active_tab == "career":
            self._render_career_tab(team)
        elif self.active_tab == "tactics":
            self._render_tactics_tab(team)

    def _switch_tab(self, key):
        self.active_tab = key
        self._render_details()

    def _render_squad_tab(self, team: Team):
        hdr = ctk.CTkFrame(self.tab_content, fg_color="#0D0D16", height=28, corner_radius=0)
        hdr.pack(fill="x", pady=(4, 0))
        hdr.pack_propagate(False)
        for txt, w in [("#", 32), ("Name", 165), ("POS", 46), ("Age", 38),
                       ("OVR", 50), ("POT", 46), ("Form", 55), ("Status", 60)]:
            ctk.CTkLabel(hdr, text=txt, font=get_font(9, "bold"), text_color=TEXT_SECONDARY,
                         width=w, anchor="w" if txt == "Name" else "center").pack(side="left")

        player_scroll = ctk.CTkScrollableFrame(self.tab_content, fg_color="transparent")
        player_scroll.pack(fill="both", expand=True)

        pos_colors = {"GK": WARNING, "DF": EMERALD, "MF": ELECTRIC_BLUE, "FW": DANGER}

        for idx, player in enumerate(team.players):
            bg = ROW_EVEN if idx % 2 == 0 else ROW_ODD
            row = ctk.CTkFrame(player_scroll, fg_color=bg, height=30, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=str(player.number), width=32, font=get_font(9),
                         text_color=TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(row, text=player.name, width=165, anchor="w",
                         font=get_font(11)).pack(side="left")
            ctk.CTkLabel(row, text=player.position, width=46, font=get_font(10, "bold"),
                         text_color=pos_colors.get(player.position, TEXT_PRIMARY)).pack(side="left")
            ctk.CTkLabel(row, text=str(player.age), width=38, font=get_font(10)).pack(side="left")

            r_color = ACCENT if player.rating >= 88 else ("#C0C0C0" if player.rating >= 83 else "#CD7F32")
            ctk.CTkLabel(row, text=str(player.rating), width=50, font=get_font(11, "bold"),
                         text_color=r_color).pack(side="left")
            ctk.CTkLabel(row, text=str(player.potential), width=46, font=get_font(10),
                         text_color=TEXT_SECONDARY).pack(side="left")

            form_color = EMERALD if player.form >= 1.0 else (WARNING if player.form >= 0.85 else DANGER)
            form_bar = ctk.CTkProgressBar(row, width=45, height=5, progress_color=form_color, fg_color="#1A1A2A")
            form_bar.set(min(1.0, player.form))
            form_bar.pack(side="left", padx=4)

            if player.injured:
                status_txt, s_color = "🏥 INJ", DANGER
            elif player.red_cards:
                status_txt, s_color = "🟥 SUS", WARNING
            else:
                status_txt, s_color = "✅ OK", EMERALD
            ctk.CTkLabel(row, text=status_txt, width=60, font=get_font(8, "bold"),
                         text_color=s_color).pack(side="left")

        ctk.CTkButton(
            self.tab_content, text="⚡  Run Training Session",
            command=lambda: self.train_team(team),
            fg_color=EMERALD, hover_color="#059669",
            corner_radius=8, font=get_font(12, "bold"), height=34
        ).pack(pady=(6, 2))
        self.training_lbl = ctk.CTkLabel(self.tab_content, text="", font=get_font(10),
                                          text_color=EMERALD)
        self.training_lbl.pack()

    def _render_career_tab(self, team: Team):
        card = ctk.CTkFrame(self.tab_content, fg_color="#0D0D16", corner_radius=12)
        card.pack(fill="x", padx=10, pady=15)

        ctk.CTkLabel(card, text="📊 Career Statistics", font=get_font(15, "bold"),
                     text_color=ACCENT).pack(pady=(14, 8))

        grid = ctk.CTkFrame(card, fg_color="transparent")
        grid.pack(pady=(0, 14))

        career_data = [
            ("🏆 Wins",      team.wins,                         EMERALD),
            ("🤝 Draws",     team.draws,                        WARNING),
            ("❌ Losses",    team.losses,                       DANGER),
            ("⚽ Goals For", team.goals_for,                    ELECTRIC_BLUE),
            ("🔒 Goals Ag.", team.goals_against,                PURPLE),
            ("📈 GD",        team.goal_difference,               ACCENT),
            ("🎯 Points",    team.points,                       ACCENT),
            ("🎮 Played",    team.matches_played,               TEXT_SECONDARY),
        ]
        for i, (label, val, color) in enumerate(career_data):
            row, col = divmod(i, 4)
            sf = ctk.CTkFrame(grid, fg_color="#131322", corner_radius=8, width=110, height=68)
            sf.grid(row=row, column=col, padx=8, pady=6)
            sf.grid_propagate(False)
            ctk.CTkLabel(sf, text=str(val), font=get_font(20, "bold"), text_color=color).pack(pady=(8, 0))
            ctk.CTkLabel(sf, text=label, font=get_font(8, "bold"), text_color=TEXT_SECONDARY).pack()

    def _render_tactics_tab(self, team: Team):
        board = TacticsBoard(self.tab_content, team,
                              on_save=lambda: self._render_details())
        board.pack(expand=True, fill="both", padx=20, pady=10)

    def train_team(self, team: Team):
        improved = 0
        for p in team.players:
            if p.rating < p.potential and random.random() < 0.3:
                p.rating += 1
                improved += 1
            p.form = min(1.2, p.form + random.uniform(0.01, 0.05))

        team.update_chemistry()
        self._render_squad_tab(team)
        self.training_lbl.configure(
            text=f"✅ Training complete — {improved} player(s) improved!"
        )
