import customtkinter as ctk
import random
from typing import List
from models.team import Team
from models.match import Match
from engine.simulator import SimulatorEngine
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, SUCCESS, BORDER_COLOR, 
                      TEXT_SECONDARY, EMERALD, DANGER, ELECTRIC_BLUE, PURPLE, WARNING,
                      ROW_EVEN, ROW_ODD)

class SeasonMode(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.fixtures = []
        self.current_fixture_idx = 0
        self.season_active = False
        self.season_stats = {}
        self.setup_ui()

    def setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        self.season_active = False
        
        # Header
        header = ctk.CTkFrame(self, fg_color=CARD_BG, height=80, corner_radius=12,
                               border_width=1, border_color=BORDER_COLOR)
        header.pack(fill="x", padx=20, pady=(20, 10))
        
        header_inner = ctk.CTkFrame(header, fg_color="transparent")
        header_inner.pack(expand=True)
        ctk.CTkLabel(header_inner, text="🗓️", font=get_font(28)).pack(side="left", padx=(0, 10))
        lbl = ctk.CTkFrame(header_inner, fg_color="transparent")
        lbl.pack(side="left")
        ctk.CTkLabel(lbl, text="SEASON MODE", font=get_font(22, "bold"), text_color=ACCENT).pack(anchor="w")
        ctk.CTkLabel(lbl, text=f"Full round-robin league — {len(self.teams)} teams", font=get_font(11), text_color=TEXT_SECONDARY).pack(anchor="w")
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Start button
        start_card = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=14, border_width=1, border_color=BORDER_COLOR)
        start_card.pack(expand=True)
        
        ctk.CTkLabel(start_card, text="🏟️", font=get_font(40)).pack(pady=(30, 10))
        ctk.CTkLabel(start_card, text="Start a New Season", font=get_font(20, "bold")).pack()
        
        total_matches = len(self.teams) * (len(self.teams) - 1)
        ctk.CTkLabel(start_card, text=f"Each team plays every other team twice (home & away)\n{total_matches} total matches", 
                     font=get_font(12), text_color=TEXT_SECONDARY, justify="center").pack(pady=10)
        
        ctk.CTkButton(start_card, text="🏆  Begin Season", command=self.start_season,
                       fg_color=ACCENT, hover_color="#B8962E", height=45, width=200, corner_radius=10,
                       font=get_font(14, "bold")).pack(pady=(10, 30))

    def start_season(self):
        self.season_active = True
        self.generate_fixtures()
        self.season_stats = {t.name: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "Pts": 0} for t in self.teams}
        self.current_fixture_idx = 0
        self.render_season()

    def generate_fixtures(self):
        """Generate round-robin fixtures (each team plays every other team twice)."""
        self.fixtures = []
        for t1 in self.teams:
            for t2 in self.teams:
                if t1 != t2:
                    self.fixtures.append((t1, t2))
        random.shuffle(self.fixtures)

    def render_season(self):
        for widget in self.content.winfo_children(): widget.destroy()
        
        # Top bar: progress
        progress_frame = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=10, height=50,
                                       border_width=1, border_color=BORDER_COLOR)
        progress_frame.pack(fill="x", pady=(0, 10))
        progress_frame.pack_propagate(False)
        
        p_inner = ctk.CTkFrame(progress_frame, fg_color="transparent")
        p_inner.pack(expand=True)
        
        played = self.current_fixture_idx
        total = len(self.fixtures)
        ctk.CTkLabel(p_inner, text=f"Matchday {played}/{total}", font=get_font(13, "bold"), text_color=ACCENT).pack(side="left", padx=10)
        
        prog_bar = ctk.CTkProgressBar(p_inner, width=300, height=8, progress_color=EMERALD, fg_color="#121220")
        prog_bar.set(played / total if total > 0 else 0)
        prog_bar.pack(side="left", padx=10)
        
        pct = round(played / total * 100) if total > 0 else 0
        ctk.CTkLabel(p_inner, text=f"{pct}%", font=get_font(11, "bold"), text_color=TEXT_SECONDARY).pack(side="left")
        
        # Two-column layout
        main = ctk.CTkFrame(self.content, fg_color="transparent")
        main.pack(fill="both", expand=True)
        
        # Left: Standings
        left = ctk.CTkFrame(main, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        left.pack(side="left", fill="both", expand=True, padx=(0, 5))
        
        ctk.CTkLabel(left, text="📊 Live Standings", font=get_font(14, "bold"), text_color=ACCENT).pack(pady=(10, 5), anchor="w", padx=15)
        
        standings_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        standings_scroll.pack(fill="both", expand=True, padx=5, pady=(0, 5))
        
        sorted_teams = sorted(self.season_stats.items(), 
                               key=lambda x: (x[1]["Pts"], x[1]["GF"] - x[1]["GA"], x[1]["GF"]), reverse=True)
        
        # Header
        hdr = ctk.CTkFrame(standings_scroll, fg_color="#0D0D16", height=25, corner_radius=0)
        hdr.pack(fill="x", pady=(0, 2))
        hdr.pack_propagate(False)
        for txt, w in [("#", 25), ("Team", 120), ("P", 25), ("W", 25), ("D", 25), ("L", 25), ("GD", 35), ("Pts", 35)]:
            ctk.CTkLabel(hdr, text=txt, font=get_font(9, "bold"), text_color=TEXT_SECONDARY, width=w, 
                         anchor="w" if txt == "Team" else "center").pack(side="left")
        
        for i, (name, s) in enumerate(sorted_teams, 1):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            row = ctk.CTkFrame(standings_scroll, fg_color=bg, height=28, corner_radius=0)
            row.pack(fill="x")
            row.pack_propagate(False)
            
            ctk.CTkLabel(row, text=str(i), width=25, font=get_font(10, "bold"), text_color=ACCENT if i <= 2 else TEXT_PRIMARY).pack(side="left")
            ctk.CTkLabel(row, text=name, width=120, anchor="w", font=get_font(10, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=str(s["P"]), width=25, font=get_font(9)).pack(side="left")
            ctk.CTkLabel(row, text=str(s["W"]), width=25, font=get_font(9), text_color=EMERALD).pack(side="left")
            ctk.CTkLabel(row, text=str(s["D"]), width=25, font=get_font(9)).pack(side="left")
            ctk.CTkLabel(row, text=str(s["L"]), width=25, font=get_font(9), text_color=DANGER).pack(side="left")
            gd = s["GF"] - s["GA"]
            gd_color = EMERALD if gd > 0 else (DANGER if gd < 0 else TEXT_SECONDARY)
            ctk.CTkLabel(row, text=f"{'+' if gd > 0 else ''}{gd}", width=35, font=get_font(9, "bold"), text_color=gd_color).pack(side="left")
            ctk.CTkLabel(row, text=str(s["Pts"]), width=35, font=get_font(10, "bold"), text_color=ACCENT).pack(side="left")
        
        # Right: Upcoming + Controls
        right = ctk.CTkFrame(main, fg_color="transparent", width=280)
        right.pack(side="right", fill="both", padx=(5, 0))
        right.pack_propagate(False)
        
        # Next fixtures
        next_frame = ctk.CTkFrame(right, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        next_frame.pack(fill="both", expand=True, pady=(0, 5))
        
        ctk.CTkLabel(next_frame, text="📋 Upcoming", font=get_font(12, "bold"), text_color=ELECTRIC_BLUE).pack(pady=(10, 5), anchor="w", padx=10)
        
        upcoming = self.fixtures[self.current_fixture_idx:self.current_fixture_idx + 6]
        for t1, t2 in upcoming:
            fix_row = ctk.CTkFrame(next_frame, fg_color="#0D0D16", height=28, corner_radius=4)
            fix_row.pack(fill="x", padx=8, pady=1)
            fix_row.pack_propagate(False)
            inner = ctk.CTkFrame(fix_row, fg_color="transparent")
            inner.pack(expand=True)
            ctk.CTkLabel(inner, text=t1.name[:12], font=get_font(9), width=90, anchor="e").pack(side="left")
            ctk.CTkLabel(inner, text=" vs ", font=get_font(8), text_color=TEXT_SECONDARY).pack(side="left")
            ctk.CTkLabel(inner, text=t2.name[:12], font=get_font(9), width=90, anchor="w").pack(side="left")
        
        # Controls
        ctrl_frame = ctk.CTkFrame(right, fg_color=CARD_BG, corner_radius=10, border_width=1, border_color=BORDER_COLOR)
        ctrl_frame.pack(fill="x", pady=(5, 0))
        
        if self.current_fixture_idx < len(self.fixtures):
            ctk.CTkButton(ctrl_frame, text="⚡ Simulate Next Match", command=self.simulate_next,
                           fg_color=EMERALD, hover_color="#059669", corner_radius=8,
                           font=get_font(12, "bold"), height=36).pack(padx=15, pady=10, fill="x")
            ctk.CTkButton(ctrl_frame, text="⏩ Simulate 5 Matches", command=lambda: self.simulate_batch(5),
                           fg_color=ELECTRIC_BLUE, hover_color="#2563EB", corner_radius=8,
                           font=get_font(11, "bold"), height=32).pack(padx=15, pady=(0, 5), fill="x")
            ctk.CTkButton(ctrl_frame, text="🏁 Simulate All Remaining", command=lambda: self.simulate_batch(len(self.fixtures)),
                           fg_color=PURPLE, hover_color="#7C3AED", corner_radius=8,
                           font=get_font(11, "bold"), height=32).pack(padx=15, pady=(0, 10), fill="x")
        else:
            self.show_season_complete()

    def simulate_next(self):
        if self.current_fixture_idx >= len(self.fixtures):
            return
        
        t1, t2 = self.fixtures[self.current_fixture_idx]
        match = Match(t1, t2)
        engine = SimulatorEngine(match)
        engine.simulate_match()
        
        s1, s2 = match.score1, match.score2
        self.season_stats[t1.name]["P"] += 1
        self.season_stats[t2.name]["P"] += 1
        self.season_stats[t1.name]["GF"] += s1
        self.season_stats[t1.name]["GA"] += s2
        self.season_stats[t2.name]["GF"] += s2
        self.season_stats[t2.name]["GA"] += s1
        
        if s1 > s2:
            self.season_stats[t1.name]["W"] += 1
            self.season_stats[t1.name]["Pts"] += 3
            self.season_stats[t2.name]["L"] += 1
        elif s2 > s1:
            self.season_stats[t2.name]["W"] += 1
            self.season_stats[t2.name]["Pts"] += 3
            self.season_stats[t1.name]["L"] += 1
        else:
            self.season_stats[t1.name]["D"] += 1
            self.season_stats[t1.name]["Pts"] += 1
            self.season_stats[t2.name]["D"] += 1
            self.season_stats[t2.name]["Pts"] += 1
        
        self.current_fixture_idx += 1
        self.render_season()

    def simulate_batch(self, count):
        for _ in range(min(count, len(self.fixtures) - self.current_fixture_idx)):
            self.simulate_next_silent()
        self.render_season()

    def simulate_next_silent(self):
        """Simulate without re-rendering (for batch)."""
        if self.current_fixture_idx >= len(self.fixtures):
            return
        
        t1, t2 = self.fixtures[self.current_fixture_idx]
        match = Match(t1, t2)
        engine = SimulatorEngine(match)
        engine.simulate_match()
        
        s1, s2 = match.score1, match.score2
        self.season_stats[t1.name]["P"] += 1
        self.season_stats[t2.name]["P"] += 1
        self.season_stats[t1.name]["GF"] += s1
        self.season_stats[t1.name]["GA"] += s2
        self.season_stats[t2.name]["GF"] += s2
        self.season_stats[t2.name]["GA"] += s1
        
        if s1 > s2:
            self.season_stats[t1.name]["W"] += 1
            self.season_stats[t1.name]["Pts"] += 3
            self.season_stats[t2.name]["L"] += 1
        elif s2 > s1:
            self.season_stats[t2.name]["W"] += 1
            self.season_stats[t2.name]["Pts"] += 3
            self.season_stats[t1.name]["L"] += 1
        else:
            self.season_stats[t1.name]["D"] += 1
            self.season_stats[t1.name]["Pts"] += 1
            self.season_stats[t2.name]["D"] += 1
            self.season_stats[t2.name]["Pts"] += 1
        
        self.current_fixture_idx += 1

    def show_season_complete(self):
        """Display when all matches have been played."""
        for widget in self.content.winfo_children(): widget.destroy()
        
        # Champion
        sorted_teams = sorted(self.season_stats.items(), 
                               key=lambda x: (x[1]["Pts"], x[1]["GF"] - x[1]["GA"]), reverse=True)
        champion = sorted_teams[0][0]
        
        trophy = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=14, border_width=2, border_color=ACCENT)
        trophy.pack(expand=True, padx=40, pady=20, fill="both")
        
        ctk.CTkLabel(trophy, text="🏆🏆🏆", font=get_font(40)).pack(pady=(30, 5))
        ctk.CTkLabel(trophy, text="SEASON CHAMPION", font=get_font(24, "bold"), text_color=ACCENT).pack()
        ctk.CTkLabel(trophy, text=champion.upper(), font=get_font(36, "bold")).pack(pady=10)
        ctk.CTkLabel(trophy, text=f"{sorted_teams[0][1]['Pts']} Points | {sorted_teams[0][1]['W']}W {sorted_teams[0][1]['D']}D {sorted_teams[0][1]['L']}L",
                     font=get_font(14), text_color=TEXT_SECONDARY).pack()
        
        # Final table
        ctk.CTkFrame(trophy, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=30, pady=15)
        ctk.CTkLabel(trophy, text="Final Standings", font=get_font(14, "bold"), text_color=TEXT_SECONDARY).pack()
        
        for i, (name, s) in enumerate(sorted_teams, 1):
            row = ctk.CTkFrame(trophy, fg_color="transparent")
            row.pack(fill="x", padx=50, pady=1)
            
            medal = "🥇" if i == 1 else ("🥈" if i == 2 else ("🥉" if i == 3 else f" {i}."))
            ctk.CTkLabel(row, text=medal, font=get_font(12), width=30).pack(side="left")
            ctk.CTkLabel(row, text=name, font=get_font(12, "bold" if i <= 3 else "normal")).pack(side="left", padx=5)
            ctk.CTkLabel(row, text=f"{s['Pts']} pts", font=get_font(11, "bold"), text_color=ACCENT).pack(side="right")
        
        ctk.CTkButton(trophy, text="🔄 New Season", command=self.setup_ui, fg_color=ACCENT,
                       hover_color="#B8962E", corner_radius=8, font=get_font(13, "bold"), height=40).pack(pady=(15, 25))
