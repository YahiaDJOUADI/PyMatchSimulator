import customtkinter as ctk
import random
from typing import List
from models.team import Team
from models.match import Match
from engine.simulator import SimulatorEngine
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, SUCCESS, BORDER_COLOR, 
                      TEXT_SECONDARY, EMERALD, DANGER, ELECTRIC_BLUE, PURPLE, CARD_HOVER)

class Tournament(ctk.CTkFrame):
    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        self.bracket = []
        self.current_round = []
        self.round_name = "Quarter-finals"
        self.all_rounds = []  # Store all rounds for bracket display
        self.setup_ui()

    def setup_ui(self):
        for widget in self.winfo_children(): widget.destroy()
        
        self.header = ctk.CTkFrame(self, fg_color=CARD_BG, height=80, corner_radius=12,
                                    border_width=1, border_color=BORDER_COLOR)
        self.header.pack(fill="x", padx=20, pady=(20, 10))
        
        header_inner = ctk.CTkFrame(self.header, fg_color="transparent")
        header_inner.pack(expand=True)
        ctk.CTkLabel(header_inner, text="🏆", font=get_font(28)).pack(side="left", padx=(0, 10))
        lbl_frame = ctk.CTkFrame(header_inner, fg_color="transparent")
        lbl_frame.pack(side="left")
        ctk.CTkLabel(lbl_frame, text="ELITE CHAMPIONS LEAGUE", font=get_font(22, "bold"), text_color=ACCENT).pack(anchor="w")
        ctk.CTkLabel(lbl_frame, text="Knockout tournament with 8 elite clubs", font=get_font(11), text_color=TEXT_SECONDARY).pack(anchor="w")
        
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=20, pady=10)
        
        self.start_btn = ctk.CTkButton(self.content, text="🎲  Generate Tournament Bracket", 
                                        command=self.generate_bracket, fg_color=ACCENT, hover_color="#B8962E",
                                        height=50, width=300, corner_radius=10, font=get_font(14, "bold"))
        self.start_btn.pack(expand=True)

    def generate_bracket(self):
        self.start_btn.pack_forget()
        self.all_rounds = []
        
        count = len(self.teams)
        if count >= 8:
            participants = 8
            self.round_name = "Quarter-finals"
        elif count >= 4:
            participants = 4
            self.round_name = "Semi-finals"
        elif count >= 2:
            participants = 2
            self.round_name = "GRAND FINAL"
        else:
            ctk.CTkLabel(self.content, text="Need at least 2 teams.", text_color=DANGER).pack()
            return

        selected_teams = random.sample(self.teams, participants)
        random.shuffle(selected_teams)
        
        self.current_round = []
        for i in range(0, participants, 2):
            self.current_round.append(Match(selected_teams[i], selected_teams[i+1]))
        
        self.render_round()

    def render_round(self):
        for widget in self.content.winfo_children(): widget.destroy()
        
        # Show bracket history + current round
        bracket_scroll = ctk.CTkScrollableFrame(self.content, fg_color="transparent")
        bracket_scroll.pack(fill="both", expand=True)
        
        # Render previous rounds
        for round_data in self.all_rounds:
            rnd_name, matches_info = round_data
            past_frame = ctk.CTkFrame(bracket_scroll, fg_color="transparent")
            past_frame.pack(fill="x", pady=5)
            ctk.CTkLabel(past_frame, text=f"✅ {rnd_name}", font=get_font(13, "bold"), text_color=TEXT_SECONDARY).pack(anchor="w", padx=10)
            
            for info in matches_info:
                row = ctk.CTkFrame(past_frame, fg_color="#0D0D16", corner_radius=8, height=35)
                row.pack(fill="x", padx=30, pady=2)
                row.pack_propagate(False)
                inner = ctk.CTkFrame(row, fg_color="transparent")
                inner.pack(expand=True)
                
                t1_color = EMERALD if info["winner"] == info["t1"] else TEXT_SECONDARY
                t2_color = EMERALD if info["winner"] == info["t2"] else TEXT_SECONDARY
                
                ctk.CTkLabel(inner, text=info["t1"], font=get_font(11, "bold"), text_color=t1_color, width=140, anchor="e").pack(side="left")
                ctk.CTkLabel(inner, text=f"  {info['result']}  ", font=get_font(12, "bold"), text_color=TEXT_PRIMARY).pack(side="left")
                ctk.CTkLabel(inner, text=info["t2"], font=get_font(11, "bold"), text_color=t2_color, width=140, anchor="w").pack(side="left")
        
        # Current round header
        ctk.CTkLabel(bracket_scroll, text=f"🔥 {self.round_name}", font=get_font(16, "bold"), text_color=ACCENT).pack(pady=(15, 8))
        
        matches_frame = ctk.CTkFrame(bracket_scroll, fg_color="transparent")
        matches_frame.pack(fill="x")
        
        for i, match in enumerate(self.current_round):
            card = ctk.CTkFrame(matches_frame, fg_color=CARD_BG, border_width=1, border_color=BORDER_COLOR, 
                                corner_radius=10, height=55)
            card.pack(pady=5, padx=60, fill="x")
            card.pack_propagate(False)
            
            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True)
            
            ctk.CTkLabel(inner, text=f"{match.team1.name}  (ELO: {match.team1.elo})", 
                         font=get_font(13, "bold"), width=220, anchor="e").pack(side="left", padx=10)
            ctk.CTkLabel(inner, text="VS", font=get_font(12, "bold"), text_color=ACCENT).pack(side="left", padx=5)
            ctk.CTkLabel(inner, text=f"(ELO: {match.team2.elo})  {match.team2.name}", 
                         font=get_font(13, "bold"), width=220, anchor="w").pack(side="left", padx=10)
            
            res_lbl = ctk.CTkLabel(inner, text="Pending", font=get_font(11), text_color=TEXT_SECONDARY)
            res_lbl.pack(side="right", padx=15)
            match.ui_label = res_lbl

        self.sim_btn = ctk.CTkButton(bracket_scroll, text=f"⚡  Simulate {self.round_name}", 
                                      command=self.simulate_round, fg_color=EMERALD, hover_color="#059669",
                                      height=42, corner_radius=8, font=get_font(13, "bold"))
        self.sim_btn.pack(pady=15)

    def simulate_round(self):
        winners = []
        round_results = []
        
        for match in self.current_round:
            engine = SimulatorEngine(match)
            engine.simulate_match()
            
            if match.penalties:
                match.ui_label.configure(text=f"{match.score1}-{match.score2} ({match.pens_score1}-{match.pens_score2} P)", text_color=SUCCESS)
                winner = match.team1 if match.pens_score1 > match.pens_score2 else match.team2
                result_str = f"{match.score1}-{match.score2} ({match.pens_score1}-{match.pens_score2}P)"
            else:
                match.ui_label.configure(text=f"{match.score1} - {match.score2}", text_color=SUCCESS)
                winner = match.team1 if match.score1 > match.score2 else match.team2
                result_str = f"{match.score1} - {match.score2}"
            
            winners.append(winner)
            round_results.append({
                "t1": match.team1.name, "t2": match.team2.name,
                "result": result_str, "winner": winner.name
            })
        
        self.all_rounds.append((self.round_name, round_results))
        self.sim_btn.configure(text="➡️  Next Round", command=lambda w=winners: self.prepare_next_round(w))

    def prepare_next_round(self, winners):
        if len(winners) == 1:
            self.show_winner(winners[0])
            return
            
        if len(winners) == 4:
            self.round_name = "Semi-finals"
        elif len(winners) == 2:
            self.round_name = "GRAND FINAL"
            
        self.current_round = []
        for i in range(0, len(winners), 2):
            self.current_round.append(Match(winners[i], winners[i+1]))
        
        self.render_round()

    def show_winner(self, team):
        for widget in self.content.winfo_children(): widget.destroy()
        
        # Trophy display
        trophy_frame = ctk.CTkFrame(self.content, fg_color=CARD_BG, corner_radius=16, 
                                     border_width=2, border_color=ACCENT)
        trophy_frame.pack(expand=True, padx=60, pady=30, fill="both")
        
        ctk.CTkLabel(trophy_frame, text="🏆🏆🏆", font=get_font(48)).pack(pady=(40, 10))
        ctk.CTkLabel(trophy_frame, text="CHAMPIONS", font=get_font(28, "bold"), text_color=ACCENT).pack()
        ctk.CTkLabel(trophy_frame, text=team.name.upper(), font=get_font(40, "bold"), text_color=TEXT_PRIMARY).pack(pady=15)
        ctk.CTkLabel(trophy_frame, text=f"ELO Rating: {team.elo}", font=get_font(14), text_color=TEXT_SECONDARY).pack()
        
        # Previous rounds summary
        if self.all_rounds:
            ctk.CTkFrame(trophy_frame, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=40, pady=20)
            ctk.CTkLabel(trophy_frame, text="Tournament Path", font=get_font(14, "bold"), text_color=TEXT_SECONDARY).pack()
            for rnd_name, matches in self.all_rounds:
                for info in matches:
                    if team.name in [info["t1"], info["t2"]]:
                        ctk.CTkLabel(trophy_frame, text=f"{rnd_name}: {info['t1']} {info['result']} {info['t2']}", 
                                     font=get_font(11), text_color=TEXT_SECONDARY).pack()
        
        ctk.CTkButton(trophy_frame, text="🔄 Play Again", command=self.setup_ui, fg_color=ACCENT,
                       hover_color="#B8962E", corner_radius=8, font=get_font(13, "bold"), height=40).pack(pady=(20, 30))
