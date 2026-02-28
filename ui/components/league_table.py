import json
import os
import customtkinter as ctk
from typing import List
from models.team import Team
from ui.theme import (CARD_BG, ACCENT, get_font, SUCCESS, BORDER_COLOR, TEXT_SECONDARY, 
                      EMERALD, DANGER, TEXT_PRIMARY, ELECTRIC_BLUE, ROW_EVEN, ROW_ODD)

class LeagueTable(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.history_file = "data/matches.json"
        self.setup_ui()

    def setup_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 5))

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.pack(side="left")
        ctk.CTkLabel(left_h, text="📊 League Standings", font=get_font(24, "bold")).pack(anchor="w")
        ctk.CTkLabel(left_h, text="Real-time rankings based on match history",
                     font=get_font(11), text_color=TEXT_SECONDARY).pack(anchor="w")

        ctk.CTkButton(header, text="🔄 Refresh", font=get_font(11), fg_color="transparent",
                       border_width=1, border_color=BORDER_COLOR, width=90, height=32,
                       corner_radius=8, command=self.refresh_table).pack(side="right")

        # Zone legend
        legend = ctk.CTkFrame(self, fg_color="transparent")
        legend.pack(fill="x", padx=30, pady=(0, 4))
        for color, label in [(EMERALD, "🏆 Champions spots"), (ELECTRIC_BLUE, "🥈 Runners-up"),
                              (DANGER, "🔻 Relegation zone")]:
            fr = ctk.CTkFrame(legend, fg_color="transparent")
            fr.pack(side="left", padx=8)
            ctk.CTkFrame(fr, fg_color=color, width=10, height=10, corner_radius=2).pack(side="left", padx=(0,4))
            ctk.CTkLabel(fr, text=label, font=get_font(9), text_color=TEXT_SECONDARY).pack(side="left")

        self.table_container = ctk.CTkFrame(self, fg_color=CARD_BG, border_width=1,
                                             border_color=BORDER_COLOR, corner_radius=12)
        self.table_container.pack(fill="both", expand=True, padx=30, pady=(0, 10))

        self.refresh_table()

    def refresh_table(self):
        for widget in self.table_container.winfo_children():
            widget.destroy()

        stats = {t.name: {"P": 0, "W": 0, "D": 0, "L": 0, "GF": 0, "GA": 0, "GD": 0, "Pts": 0, "form": []} 
                 for t in self.teams}
        
        if os.path.exists(self.history_file):
            with open(self.history_file, "r") as f:
                data = json.load(f)
                for m in data.get("matches", []):
                    t1, t2 = m["team1"], m["team2"]
                    s1, s2 = m["score1"], m["score2"]
                    
                    if t1 in stats and t2 in stats:
                        stats[t1]["P"] += 1
                        stats[t2]["P"] += 1
                        stats[t1]["GF"] += s1
                        stats[t1]["GA"] += s2
                        stats[t2]["GF"] += s2
                        stats[t2]["GA"] += s1
                        
                        if s1 > s2:
                            stats[t1]["W"] += 1
                            stats[t1]["Pts"] += 3
                            stats[t2]["L"] += 1
                            stats[t1]["form"].append("W")
                            stats[t2]["form"].append("L")
                        elif s2 > s1:
                            stats[t2]["W"] += 1
                            stats[t2]["Pts"] += 3
                            stats[t1]["L"] += 1
                            stats[t1]["form"].append("L")
                            stats[t2]["form"].append("W")
                        else:
                            stats[t1]["D"] += 1
                            stats[t1]["Pts"] += 1
                            stats[t2]["D"] += 1
                            stats[t2]["Pts"] += 1
                            stats[t1]["form"].append("D")
                            stats[t2]["form"].append("D")

        for team in stats:
            stats[team]["GD"] = stats[team]["GF"] - stats[team]["GA"]

        sorted_teams = sorted(stats.items(), key=lambda x: (x[1]["Pts"], x[1]["GD"], x[1]["GF"]), reverse=True)

        # Draw Header
        header = ctk.CTkFrame(self.table_container, fg_color="#0D0D16", height=40, corner_radius=0)
        header.pack(fill="x", padx=2, pady=(2, 0))
        header.pack_propagate(False)
        
        cols = [("#", 35), ("Team", 160), ("P", 35), ("W", 35), ("D", 35), ("L", 35),
                ("GF", 35), ("GA", 35), ("GD", 40), ("Pts", 45), ("ELO", 50), ("Form", 100)]
        for txt, width in cols:
            ctk.CTkLabel(header, text=txt, font=get_font(10, "bold"), text_color=TEXT_SECONDARY,
                         width=width, anchor="w" if txt == "Team" else "center").pack(side="left")

        # Draw Rows
        total = len(sorted_teams)
        for i, (name, s) in enumerate(sorted_teams, 1):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            
            # Zone color: top 1 = champion, top 2-3 = runners-up, bottom = relegation
            if i == 1:
                left_accent = EMERALD
            elif i <= 3:
                left_accent = ELECTRIC_BLUE
            elif i == total:
                left_accent = DANGER
            else:
                left_accent = "transparent"
            
            row = ctk.CTkFrame(self.table_container, fg_color=bg, height=38, corner_radius=0)
            row.pack(fill="x", padx=2, pady=0)
            row.pack_propagate(False)
            
            # Position indicator
            indicator = ctk.CTkFrame(row, width=3, fg_color=left_accent, corner_radius=0)
            indicator.pack(side="left", fill="y")
            
            pos_color = ACCENT if i <= 3 else TEXT_PRIMARY
            ctk.CTkLabel(row, text=str(i), width=32, font=get_font(12, "bold"), text_color=pos_color).pack(side="left")
            ctk.CTkLabel(row, text=name, width=160, anchor="w", font=get_font(13, "bold")).pack(side="left")
            ctk.CTkLabel(row, text=str(s["P"]), width=35, font=get_font(11)).pack(side="left")
            ctk.CTkLabel(row, text=str(s["W"]), width=35, font=get_font(11), text_color=EMERALD).pack(side="left")
            ctk.CTkLabel(row, text=str(s["D"]), width=35, font=get_font(11)).pack(side="left")
            ctk.CTkLabel(row, text=str(s["L"]), width=35, font=get_font(11), text_color=DANGER).pack(side="left")
            ctk.CTkLabel(row, text=str(s["GF"]), width=35, font=get_font(11)).pack(side="left")
            ctk.CTkLabel(row, text=str(s["GA"]), width=35, font=get_font(11)).pack(side="left")
            
            gd = s["GD"]
            gd_color = EMERALD if gd > 0 else (DANGER if gd < 0 else TEXT_SECONDARY)
            gd_text = f"+{gd}" if gd > 0 else str(gd)
            ctk.CTkLabel(row, text=gd_text, width=40, font=get_font(11, "bold"), text_color=gd_color).pack(side="left")
            ctk.CTkLabel(row, text=str(s["Pts"]), width=45, font=get_font(14, "bold"), text_color=ACCENT).pack(side="left")

            # ELO column
            team_obj = next((t for t in self.teams if t.name == name), None)
            elo_val = str(team_obj.elo) if team_obj else "—"
            ctk.CTkLabel(row, text=elo_val, width=50, font=get_font(10, "bold"),
                         text_color=ELECTRIC_BLUE if i <= 3 else TEXT_SECONDARY).pack(side="left")
            
            # Form column — last 5 results as colored dots
            form_frame = ctk.CTkFrame(row, fg_color="transparent", width=100)
            form_frame.pack(side="left")
            
            last_5 = s["form"][-5:]
            for result in last_5:
                if result == "W":
                    dot_color = EMERALD
                    dot_text = "W"
                elif result == "L":
                    dot_color = DANGER
                    dot_text = "L"
                else:
                    dot_color = TEXT_SECONDARY
                    dot_text = "D"
                dot = ctk.CTkLabel(form_frame, text=dot_text, font=get_font(8, "bold"), text_color="#000000",
                                   fg_color=dot_color, width=16, height=16, corner_radius=3)
                dot.pack(side="left", padx=1)
