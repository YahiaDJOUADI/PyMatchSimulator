import json
import os
from typing import List

import customtkinter as ctk

from models.team import Team
from models.player import Player
from ui.theme import setup_theme, BACKGROUND, TEXT_PRIMARY, get_font, ACCENT, TEXT_SECONDARY, BORDER_COLOR
from ui.components.sidebar import Sidebar
from ui.components.match_simulator import MatchSimulator
from ui.components.team_manager import TeamManager
from ui.components.match_history import MatchHistory
from ui.components.league_table import LeagueTable
from ui.components.tournament import Tournament
from ui.components.dashboard import Dashboard
from ui.components.awards import AwardsView
from ui.components.season import SeasonMode
from ui.components.player_rankings import PlayerRankings
from ui.components.transfer_market import TransferMarket


class FootballSimulatorUI:
    def __init__(self):
        setup_theme()

        self.root = ctk.CTk()
        self.root.title("PyMatch Simulator")
        self.root.geometry("1340x820")
        self.root.minsize(1100, 720)
        self.root.configure(fg_color=BACKGROUND)

        from utils.data_loader import load_teams
        self.teams = load_teams()

        self.sidebar = Sidebar(self.root, on_change_view=self.switch_view)
        self.sidebar.pack(side="left", fill="y")

        self.container = ctk.CTkFrame(self.root, fg_color="transparent")
        self.container.pack(side="right", fill="both", expand=True)

        self.views = {}
        self.current_view = None

        self.views["dashboard"]       = Dashboard(
            self.container, self.teams,
            on_quick_match=lambda: self.switch_view("match"),
            on_start_season=lambda: self.switch_view("season"),
        )
        self.views["match"]           = MatchSimulator(self.container, self.teams)
        self.views["team_manager"]    = TeamManager(self.container, self.teams)
        self.views["match_history"]   = MatchHistory(self.container)
        self.views["league_table"]    = LeagueTable(self.container, self.teams)
        self.views["tournament"]      = Tournament(self.container, self.teams)
        self.views["awards"]          = AwardsView(self.container)
        self.views["season"]          = SeasonMode(self.container, self.teams)
        self.views["rankings"]        = PlayerRankings(self.container, self.teams)
        self.views["transfer_market"] = TransferMarket(self.container, self.teams)

        self.switch_view("dashboard")
        self.root.mainloop()

    def switch_view(self, view_id: str):
        if self.current_view:
            self.current_view.pack_forget()

        self.sidebar.set_active(view_id)

        if view_id in self.views:
            self.current_view = self.views[view_id]

            if hasattr(self.current_view, "refresh"):
                try:
                    self.current_view.refresh()
                except Exception:
                    pass
            elif hasattr(self.current_view, "refresh_table"):
                try:
                    self.current_view.refresh_table()
                except Exception:
                    pass
            elif hasattr(self.current_view, "load_history"):
                try:
                    self.current_view.load_history()
                except Exception:
                    pass

            self.current_view.pack(fill="both", expand=True)
        else:
            placeholder = ctk.CTkFrame(self.container, fg_color="transparent")
            ctk.CTkLabel(
                placeholder,
                text=f"⚙️  View '{view_id}' is under development.",
                font=get_font(20), text_color=TEXT_SECONDARY
            ).pack(expand=True)
            self.current_view = placeholder
            self.current_view.pack(fill="both", expand=True)