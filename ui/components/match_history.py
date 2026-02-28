import customtkinter as ctk
import json
import os
from ui.theme import (CARD_BG, ACCENT, get_font, DANGER, BORDER_COLOR,
                      TEXT_SECONDARY, EMERALD, TEXT_PRIMARY, WARNING, ROW_EVEN, ROW_ODD,
                      ELECTRIC_BLUE, PURPLE)


class MatchHistory(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        self.history_file = "data/matches.json"
        self.setup_ui()

    def setup_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(20, 8))

        ctk.CTkLabel(header, text="📜 Match History", font=get_font(24, "bold")).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(btn_row, text="🔄 Refresh", font=get_font(11),
                       fg_color="transparent", border_width=1, border_color=BORDER_COLOR,
                       width=90, height=30, corner_radius=6,
                       command=self.load_history).pack(side="left", padx=(0, 8))

        ctk.CTkButton(btn_row, text="🗑️ Clear", font=get_font(11),
                       fg_color="transparent", border_width=1, border_color=DANGER,
                       text_color=DANGER, hover_color="#2A1520", width=80, height=30,
                       corner_radius=6, command=self.clear_history).pack(side="left")

        # Column header bar
        col_hdr = ctk.CTkFrame(self, fg_color="#0D0D16", height=30, corner_radius=0)
        col_hdr.pack(fill="x", padx=30, pady=(6, 0))
        col_hdr.pack_propagate(False)

        for txt, w, anchor in [
            ("#",       28, "center"),
            ("",        26, "center"),   # weather
            ("Home",   140, "w"),
            ("Score",   70, "center"),
            ("Away",   140, "w"),
            ("MOTM",   130, "w"),
            ("Pens",    70, "center"),
            ("VAR",     40, "center"),
            ("Shots",   90, "center"),
        ]:
            ctk.CTkLabel(col_hdr, text=txt, font=get_font(9, "bold"), text_color=TEXT_SECONDARY,
                         width=w, anchor=anchor).pack(side="left")

        # Scrollable list
        self.scroll = ctk.CTkScrollableFrame(self, fg_color=CARD_BG, border_width=1,
                                              border_color=BORDER_COLOR, corner_radius=12)
        self.scroll.pack(fill="both", expand=True, padx=30, pady=(0, 15))
        self.load_history()

    # ─────────────────────────────────────
    def load_history(self):
        for widget in self.scroll.winfo_children():
            widget.destroy()

        if not os.path.exists(self.history_file):
            self._empty()
            return

        with open(self.history_file, "r") as f:
            data = json.load(f)
        matches = data.get("matches", [])

        if not matches:
            self._empty()
            return

        total_goals = sum(m["score1"] + m["score2"] for m in matches)
        avg_goals = round(total_goals / len(matches), 1)
        penalties = sum(1 for m in matches if m.get("penalties"))

        # Summary bar
        summary = ctk.CTkFrame(self.scroll, fg_color="#0B0B16", height=36, corner_radius=8)
        summary.pack(fill="x", padx=5, pady=(6, 8))
        summary.pack_propagate(False)
        s_inner = ctk.CTkFrame(summary, fg_color="transparent")
        s_inner.pack(expand=True)
        for val, label, color in [
            (str(len(matches)), "matches", ACCENT),
            (str(avg_goals), "avg goals/game", EMERALD),
            (str(penalties), "went to penalties", WARNING),
        ]:
            ctk.CTkLabel(s_inner, text=f" {val} ", font=get_font(13, "bold"), text_color=color).pack(side="left")
            ctk.CTkLabel(s_inner, text=f"{label}  |  ", font=get_font(10),
                         text_color=TEXT_SECONDARY).pack(side="left")

        for i, match in enumerate(reversed(matches)):
            bg = ROW_EVEN if i % 2 == 0 else ROW_ODD
            card = ctk.CTkFrame(self.scroll, fg_color=bg, height=46, corner_radius=6)
            card.pack(fill="x", pady=1, padx=4)
            card.pack_propagate(False)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(expand=True, fill="x", padx=6)

            t1, t2 = match["team1"], match["team2"]
            s1, s2 = match["score1"], match["score2"]

            # Row number
            ctk.CTkLabel(inner, text=str(len(matches) - i), font=get_font(9),
                         text_color=TEXT_SECONDARY, width=28, anchor="center").pack(side="left")

            # Weather
            weather_icon = match.get("weather", "").split(" ")[0]
            ctk.CTkLabel(inner, text=weather_icon or "—", font=get_font(12), width=26).pack(side="left")

            # Team 1
            ctk.CTkLabel(inner, text=t1, font=get_font(12, "bold"), width=140, anchor="w").pack(side="left")

            # Score
            score_color = EMERALD if s1 > s2 else (DANGER if s1 < s2 else TEXT_SECONDARY)
            ctk.CTkLabel(inner, text=f"{s1} – {s2}", font=get_font(14, "bold"),
                         text_color=score_color, width=70, anchor="center").pack(side="left")

            # Team 2
            ctk.CTkLabel(inner, text=t2, font=get_font(12, "bold"), width=140, anchor="w").pack(side="left")

            # MOTM
            motm = match.get("motm", "")
            ctk.CTkLabel(inner, text=f"⭐ {motm[:14]}" if motm else "—", font=get_font(9),
                         text_color=ACCENT if motm else TEXT_SECONDARY, width=130).pack(side="left")

            # Penalties
            if match.get("penalties"):
                ps1, ps2 = match.get("pens_score1", "?"), match.get("pens_score2", "?")
                pen_text = f"🎯 {ps1}–{ps2}"
            else:
                pen_text = "—"
            ctk.CTkLabel(inner, text=pen_text, font=get_font(9),
                         text_color=WARNING if match.get("penalties") else TEXT_SECONDARY,
                         width=70).pack(side="left")

            # VAR
            var_count = match.get("var_decisions", 0)
            ctk.CTkLabel(inner, text=f"📺{var_count}" if var_count else "—",
                         font=get_font(9), text_color=ELECTRIC_BLUE if var_count else TEXT_SECONDARY,
                         width=40).pack(side="left")

            # Shots on target (new field, graceful fallback)
            st1 = match.get("shots_on_target1", "")
            st2 = match.get("shots_on_target2", "")
            shots_text = f"🎯 {st1}–{st2}" if st1 != "" else "—"
            ctk.CTkLabel(inner, text=shots_text, font=get_font(9),
                         text_color=PURPLE if st1 != "" else TEXT_SECONDARY, width=90).pack(side="left")

    def _empty(self):
        ctk.CTkLabel(self.scroll, text="No match history found.\nPlay some matches!",
                     font=get_font(14), text_color=TEXT_SECONDARY, justify="center").pack(pady=60)

    def clear_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "w") as f:
                json.dump({"matches": []}, f, indent=4)
        self.load_history()
