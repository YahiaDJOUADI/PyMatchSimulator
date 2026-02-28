import customtkinter as ctk
from models.team import Team, FORMATIONS
from ui.theme import (CARD_BG, ACCENT, TEXT_PRIMARY, get_font, TEXT_SECONDARY,
                      BORDER_COLOR, EMERALD, ELECTRIC_BLUE, DANGER, WARNING, PURPLE)


FORMATION_DETAILS = {
    "4-4-2":          ("⚖️ Classic & Balanced", "No modifiers — solid all-round shape."),
    "4-3-3":          ("⚔️ Attacking Press",   "+15% ATK | -5% MID | -10% DEF"),
    "5-3-2":          ("🛡️ Park the Bus",       "+15% DEF | -15% ATK"),
    "3-5-2":          ("🎯 Midfield Engine",    "+15% MID | +5% ATK | -20% DEF"),
    "4-5-1":          ("🎮 Possession Control", "+20% MID | -10% ATK | -5% DEF"),
    "4-2-3-1":        ("🔥 Modern Balanced",    "+10% ATK | +5% MID | -5% DEF"),
    "3-4-3":          ("💥 Total Attack",       "+20% ATK | -25% DEF"),
    "4-1-4-1":        ("🧠 Deep Block",         "+10% MID | +5% DEF | -5% ATK"),
    "5-4-1":          ("🏰 Ultra Defensive",    "+20% DEF | +10% MID | -20% ATK"),
    "4-4-2 Diamond":  ("💎 Diamond Midfield",   "+12% ATK | +12% MID | -8% DEF"),
}

# ATK/DEF color arrows
def _bonus_label(val):
    if val > 1.0:
        return f"▲ {round((val-1)*100)}%", EMERALD
    elif val < 1.0:
        return f"▼ {round((1-val)*100)}%", DANGER
    else:
        return "—", TEXT_SECONDARY


class TacticsBoard(ctk.CTkFrame):
    def __init__(self, master, team: Team, on_save, **kwargs):
        super().__init__(master, fg_color="#090915", border_width=2, border_color=ACCENT,
                         corner_radius=16, **kwargs)
        self.team = team
        self.on_save = on_save
        self.setup_ui()

    def setup_ui(self):
        ctk.CTkLabel(self, text="⚙️  TACTICAL BOARD", font=get_font(17, "bold"),
                     text_color=ACCENT).pack(pady=(18, 3))
        ctk.CTkLabel(self, text=self.team.name, font=get_font(13, "bold"),
                     text_color=TEXT_PRIMARY).pack(pady=(0, 8))

        # Morale indicator
        morale_row = ctk.CTkFrame(self, fg_color="transparent")
        morale_row.pack(fill="x", padx=28, pady=(0, 8))
        morale_color = EMERALD if self.team.morale >= 1.0 else (WARNING if self.team.morale >= 0.75 else DANGER)
        ctk.CTkLabel(morale_row, text=f"Morale: {self.team.get_morale_label()}",
                     font=get_font(11), text_color=morale_color).pack(side="left")
        bar = ctk.CTkProgressBar(morale_row, width=90, height=6, progress_color=morale_color, fg_color="#1A1A2A")
        bar.set(min(1.0, self.team.morale / 1.5))
        bar.pack(side="left", padx=10)

        # Formation selector
        ctk.CTkLabel(self, text="Formation", font=get_font(11, "bold"),
                     text_color=TEXT_SECONDARY).pack()

        self.formation_var = ctk.StringVar(value=self.team.formation)
        self.combo = ctk.CTkComboBox(self, values=list(FORMATION_DETAILS.keys()),
                                      variable=self.formation_var, command=self._on_change,
                                      width=220, height=32, corner_radius=8)
        self.combo.pack(pady=6)

        # Preview panel
        self.preview_frame = ctk.CTkFrame(self, fg_color="#0E0E1C", corner_radius=10)
        self.preview_frame.pack(fill="x", padx=24, pady=8)
        self._build_preview(self.team.formation)

        # Bonus stat bars
        self.bars_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.bars_frame.pack(fill="x", padx=24, pady=4)
        self._build_bonus_bars(self.team.formation)

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", pady=12, padx=24)
        ctk.CTkButton(btn_frame, text="✅ Apply", command=self._apply,
                       fg_color=EMERALD, hover_color="#059669", corner_radius=8,
                       font=get_font(12, "bold")).pack(side="left", expand=True, padx=(0, 5))
        ctk.CTkButton(btn_frame, text="✕ Cancel", command=self.destroy,
                       fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
                       corner_radius=8, font=get_font(12)).pack(side="right", expand=True, padx=(5, 0))

    def _on_change(self, formation):
        for w in self.preview_frame.winfo_children():
            w.destroy()
        for w in self.bars_frame.winfo_children():
            w.destroy()
        self._build_preview(formation)
        self._build_bonus_bars(formation)

    def _build_preview(self, formation):
        name, desc = FORMATION_DETAILS.get(formation, ("?", ""))
        ctk.CTkLabel(self.preview_frame, text=name, font=get_font(12, "bold"),
                     text_color=ACCENT).pack(pady=(8, 2))
        ctk.CTkLabel(self.preview_frame, text=desc, font=get_font(10),
                     text_color=TEXT_SECONDARY, justify="center").pack(pady=(0, 8))

    def _build_bonus_bars(self, formation):
        atk_b, mid_b, def_b = FORMATIONS.get(formation, (1.0, 1.0, 1.0))
        labels = [("ATK", atk_b, DANGER), ("MID", ELECTRIC_BLUE, mid_b), ("DEF", EMERALD, def_b)]
        labels = [("ATK", atk_b, DANGER), ("MID", mid_b, ELECTRIC_BLUE), ("DEF", def_b, EMERALD)]

        for stat, val, color in labels:
            row = ctk.CTkFrame(self.bars_frame, fg_color="transparent")
            row.pack(fill="x", pady=2)
            ctk.CTkLabel(row, text=stat, font=get_font(10, "bold"), text_color=TEXT_SECONDARY, width=35).pack(side="left")
            bar = ctk.CTkProgressBar(row, width=120, height=6, progress_color=color, fg_color="#1A1A2A")
            bar.set(min(1.0, val / 1.25))
            bar.pack(side="left", padx=6)
            txt, txt_color = _bonus_label(val)
            ctk.CTkLabel(row, text=txt, font=get_font(9, "bold"), text_color=txt_color, width=45).pack(side="left")

    def _apply(self):
        self.team.formation = self.formation_var.get()
        self.on_save()
        self.destroy()
