import random
import customtkinter as ctk
from typing import List
from models.team import Team
from ui.theme import (CARD_BG, ACCENT, ACCENT_DARK, TEXT_PRIMARY, get_font, TEXT_SECONDARY,
                      BORDER_COLOR, EMERALD, EMERALD_DARK, DANGER, ELECTRIC_BLUE, PURPLE,
                      WARNING, ORANGE, NEON_CYAN, ROW_EVEN, ROW_ODD, SUCCESS)


class TransferMarket(ctk.CTkFrame):
    """
    Transfer Market — buy/sell players between teams.
    Each team has a budget. Transfer listed players can be bought for their market value.
    """

    TEAM_BUDGET = 150   # default budget in €M per team (persistent in session)

    def __init__(self, master, teams: List[Team], **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.teams = teams
        # Init budgets (session-only)
        for t in teams:
            if not hasattr(t, "budget"):
                t.budget = self.TEAM_BUDGET
        self.selected_player = None
        self.selected_player_team = None
        self.active_filter = "All"
        self.setup_ui()

    # ──────────────────────────────────────────────
    def setup_ui(self):
        # ── Header ──
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", padx=28, pady=(18, 6))
        ctk.CTkLabel(hdr, text="💰 Transfer Market", font=get_font(24, "bold"),
                     text_color=TEXT_PRIMARY).pack(side="left")
        ctk.CTkLabel(hdr, text="Buy talents, build your empire",
                     font=get_font(11), text_color=TEXT_SECONDARY).pack(side="left", padx=14, pady=(4, 0))

        # Refresh button
        ctk.CTkButton(hdr, text="🔄 Refresh Listings", font=get_font(11),
                       fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
                       width=130, height=32, corner_radius=8,
                       command=self.refresh).pack(side="right")

        # ── Main split ──
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=20, pady=4)

        # Left: player listings
        left = ctk.CTkFrame(split, fg_color=CARD_BG, border_width=1,
                             border_color=BORDER_COLOR, corner_radius=12)
        left.pack(side="left", fill="both", expand=True, padx=(0, 8))

        # Filter + search bar
        ctrl_bar = ctk.CTkFrame(left, fg_color="transparent")
        ctrl_bar.pack(fill="x", padx=12, pady=10)

        ctk.CTkLabel(ctrl_bar, text="Position:", font=get_font(10),
                     text_color=TEXT_SECONDARY).pack(side="left")
        for pos in ["All", "GK", "DF", "MF", "FW"]:
            b = ctk.CTkButton(ctrl_bar, text=pos, width=44, height=26,
                               fg_color=ACCENT if pos == self.active_filter else "transparent",
                               border_width=1, border_color=BORDER_COLOR, corner_radius=6,
                               font=get_font(10, "bold"),
                               command=lambda p=pos: self._set_filter(p))
            b.pack(side="left", padx=2)

        self.search_var = ctk.StringVar()
        self.search_var.trace("w", lambda *_: self._render_listings())
        ctk.CTkEntry(ctrl_bar, textvariable=self.search_var, placeholder_text="🔍 Search player…",
                     height=28, width=150, fg_color="#0D0D1A",
                     border_color=BORDER_COLOR, corner_radius=8).pack(side="right")

        # Table header
        th = ctk.CTkFrame(left, fg_color="#0A0A18", height=26, corner_radius=0)
        th.pack(fill="x")
        th.pack_propagate(False)
        for txt, w in [("Player", 160), ("Team", 120), ("POS", 50),
                       ("Age", 40), ("OVR", 48), ("Value", 72), ("Action", 80)]:
            ctk.CTkLabel(th, text=txt, font=get_font(9, "bold"), text_color=TEXT_SECONDARY,
                         width=w, anchor="w" if txt in ("Player", "Team") else "center"
                         ).pack(side="left", padx=2)

        self.listing_scroll = ctk.CTkScrollableFrame(left, fg_color="transparent")
        self.listing_scroll.pack(fill="both", expand=True, padx=4, pady=4)
        self._render_listings()

        # Right: deal panel + team budgets
        right = ctk.CTkFrame(split, fg_color="transparent", width=270)
        right.pack(side="right", fill="both", padx=(8, 0))
        right.pack_propagate(False)

        # Player detail card
        self.detail_card = ctk.CTkFrame(right, fg_color=CARD_BG, border_width=1,
                                         border_color=BORDER_COLOR, corner_radius=12)
        self.detail_card.pack(fill="x", pady=(0, 8))
        self._render_detail_placeholder()

        # Team finances
        fin_card = ctk.CTkFrame(right, fg_color=CARD_BG, border_width=1,
                                 border_color=BORDER_COLOR, corner_radius=12)
        fin_card.pack(fill="both", expand=True)

        ctk.CTkLabel(fin_card, text="🏦 Team Finances", font=get_font(13, "bold")).pack(
            pady=(12, 6), padx=14, anchor="w"
        )
        self.finance_scroll = ctk.CTkScrollableFrame(fin_card, fg_color="transparent")
        self.finance_scroll.pack(fill="both", expand=True, padx=8, pady=(0, 8))
        self._render_finances()

    # ──────────────────────────────────────────────
    def _set_filter(self, pos: str):
        self.active_filter = pos
        self._render_listings()

    def _render_listings(self):
        for w in self.listing_scroll.winfo_children():
            w.destroy()

        query = self.search_var.get().lower()
        pos_colors = {"GK": WARNING, "DF": EMERALD, "MF": ELECTRIC_BLUE, "FW": DANGER}

        all_players = []
        for team in self.teams:
            for player in team.players:
                if self.active_filter != "All" and player.position != self.active_filter:
                    continue
                if query and query not in player.name.lower() and query not in team.name.lower():
                    continue
                all_players.append((player, team))

        # Sort by market value descending
        all_players.sort(key=lambda x: x[0].market_value, reverse=True)

        for i, (player, team) in enumerate(all_players):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            row = ctk.CTkFrame(self.listing_scroll, fg_color=bg, height=32, corner_radius=0)
            row.pack(fill="x", pady=0)
            row.pack_propagate(False)

            ctk.CTkLabel(row, text=player.name, width=160, font=get_font(11), anchor="w").pack(side="left", padx=2)
            ctk.CTkLabel(row, text=team.name[:14], width=120, font=get_font(10),
                         text_color=TEXT_SECONDARY, anchor="w").pack(side="left")
            ctk.CTkLabel(row, text=player.position, width=50, font=get_font(10, "bold"),
                         text_color=pos_colors.get(player.position, TEXT_PRIMARY)).pack(side="left")
            ctk.CTkLabel(row, text=str(player.age), width=40, font=get_font(10)).pack(side="left")
            ctk.CTkLabel(row, text=str(player.rating), width=48, font=get_font(11, "bold"),
                         text_color=ACCENT).pack(side="left")
            ctk.CTkLabel(row, text=player.get_value_str(), width=72, font=get_font(10, "bold"),
                         text_color=NEON_CYAN).pack(side="left")

            ctk.CTkButton(row, text="👁 View", width=76, height=26,
                           fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
                           corner_radius=6, font=get_font(9),
                           command=lambda p=player, t=team: self._select_player(p, t)
                           ).pack(side="left", padx=2)

            # Hover highlight
            row.bind("<Enter>", lambda e, r=row, bg=bg: r.configure(fg_color="#1A1A30"))
            row.bind("<Leave>", lambda e, r=row, bg=bg: r.configure(fg_color=bg))

    def _select_player(self, player, team):
        self.selected_player = player
        self.selected_player_team = team
        self._render_detail_card(player, team)

    def _render_detail_placeholder(self):
        for w in self.detail_card.winfo_children():
            w.destroy()
        ctk.CTkLabel(self.detail_card, text="Select a player\nto view details",
                     font=get_font(12), text_color=TEXT_SECONDARY).pack(pady=30)

    def _render_detail_card(self, player, team):
        for w in self.detail_card.winfo_children():
            w.destroy()

        pos_colors = {"GK": WARNING, "DF": EMERALD, "MF": ELECTRIC_BLUE, "FW": DANGER}
        pc = pos_colors.get(player.position, TEXT_PRIMARY)

        ctk.CTkLabel(self.detail_card, text=f"{player.get_position_emoji()} {player.name}",
                     font=get_font(15, "bold")).pack(pady=(12, 2), padx=14, anchor="w")
        ctk.CTkLabel(self.detail_card, text=f"{team.name}  ·  {player.position}  ·  Age {player.age}",
                     font=get_font(10), text_color=TEXT_SECONDARY).pack(padx=14, anchor="w")

        # Stats mini-grid
        sg = ctk.CTkFrame(self.detail_card, fg_color="#0D0D1A", corner_radius=8)
        sg.pack(fill="x", padx=12, pady=8)

        data = [
            ("⭐ OVR",     str(player.rating),          ACCENT),
            ("🌟 POT",     str(player.potential),        ELECTRIC_BLUE),
            ("💰 Value",   player.get_value_str(),        NEON_CYAN),
            ("📈 Form",    player.get_form_label(),        EMERALD),
            ("🦶 Foot",    player.preferred_foot,         TEXT_PRIMARY),
            ("🌟 Skills",  f"{player.skill_moves}★",      PURPLE),
        ]
        for j, (lbl, val, col) in enumerate(data):
            r, c = divmod(j, 2)
            cell = ctk.CTkFrame(sg, fg_color="transparent")
            cell.grid(row=r, column=c, padx=10, pady=4, sticky="w")
            ctk.CTkLabel(cell, text=lbl, font=get_font(8), text_color=TEXT_SECONDARY).pack(anchor="w")
            ctk.CTkLabel(cell, text=val, font=get_font(11, "bold"), text_color=col).pack(anchor="w")
        sg.columnconfigure((0, 1), weight=1)

        # Buy controls
        buy_row = ctk.CTkFrame(self.detail_card, fg_color="transparent")
        buy_row.pack(fill="x", padx=12, pady=(2, 4))
        ctk.CTkLabel(buy_row, text="Buy for team:", font=get_font(9),
                     text_color=TEXT_SECONDARY).pack(anchor="w")

        self.buy_team_var = ctk.StringVar(
            value=next((t.name for t in self.teams if t != team), self.teams[0].name)
        )
        other_teams = [t.name for t in self.teams if t != team]
        if other_teams:
            ctk.CTkComboBox(buy_row, values=other_teams, variable=self.buy_team_var,
                             width=220, height=28).pack(fill="x", pady=4)
            ctk.CTkButton(buy_row, text=f"💸 Buy for {player.get_value_str()}",
                           fg_color=EMERALD, hover_color=EMERALD_DARK,
                           corner_radius=8, font=get_font(12, "bold"), height=34,
                           command=lambda: self._execute_transfer(player, team)
                           ).pack(fill="x", pady=(2, 8))

        self.transfer_msg = ctk.CTkLabel(self.detail_card, text="", font=get_font(10),
                                          text_color=EMERALD, wraplength=235)
        self.transfer_msg.pack(pady=(0, 4))

    def _execute_transfer(self, player, from_team):
        target_name = self.buy_team_var.get()
        target_team = next((t for t in self.teams if t.name == target_name), None)
        if not target_team:
            return

        cost = player.market_value
        if target_team.budget < cost:
            self.transfer_msg.configure(
                text=f"❌ Insufficient budget!\n{target_name} has €{target_team.budget}M",
                text_color=DANGER
            )
            return

        # Execute transfer
        from_team.players.remove(player)
        target_team.players.append(player)
        target_team.budget -= cost
        from_team.budget += round(cost * 0.9)   # selling team gets 90%

        # Recalculate team overall
        from_team.overall_rating  = from_team._calculate_overall()
        target_team.overall_rating = target_team._calculate_overall()

        self.transfer_msg.configure(
            text=f"✅ {player.name} → {target_name}!\nCost: {player.get_value_str()}",
            text_color=EMERALD
        )
        self._render_listings()
        self._render_finances()

    def _render_finances(self):
        for w in self.finance_scroll.winfo_children():
            w.destroy()

        sorted_teams = sorted(self.teams, key=lambda t: getattr(t, "budget", 0), reverse=True)
        for team in sorted_teams:
            budget = getattr(team, "budget", self.TEAM_BUDGET)
            max_budget = self.TEAM_BUDGET * 2
            pct = min(1.0, budget / max_budget)
            color = EMERALD if budget >= 80 else (WARNING if budget >= 30 else DANGER)

            row = ctk.CTkFrame(self.finance_scroll, fg_color=CARD_BG if budget > 50 else "#0E0010",
                                corner_radius=6)
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=team.name, font=get_font(10, "bold"), anchor="w",
                         width=140).pack(side="left", padx=8, pady=5)
            bar = ctk.CTkProgressBar(row, width=70, height=7, progress_color=color,
                                      fg_color="#1A1A2A")
            bar.set(pct)
            bar.pack(side="left", padx=4)
            ctk.CTkLabel(row, text=f"€{budget}M", font=get_font(10, "bold"),
                         text_color=color).pack(side="right", padx=8)

    def refresh(self):
        for w in self.winfo_children():
            w.destroy()
        self.setup_ui()
