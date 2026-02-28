import random
import customtkinter as ctk

# Pitch dimensions
PW, PH = 560, 260

class PitchCanvas(ctk.CTkCanvas):
    """
    A standalone canvas that handles drawing the football pitch and animating the ball
    based on match events.
    """
    def __init__(self, master, **kwargs):
        super().__init__(master, width=PW, height=PH, bg="#091F0D", highlightthickness=0, **kwargs)
        self.draw_pitch()
        self.ball = self.create_oval(
            PW // 2 - 6, PH // 2 - 6, PW // 2 + 6, PH // 2 + 6,
            fill="white", outline="#DDDDDD", width=1
        )

    def draw_pitch(self):
        c = self
        W, H = PW, PH
        stripe_w = W // 10
        for i in range(10):
            color = "#0B2413" if i % 2 == 0 else "#091F0D"
            c.create_rectangle(i * stripe_w, 0, (i + 1) * stripe_w, H, fill=color, outline="")

        lc = "#2E8B4E"
        c.create_rectangle(4, 4, W - 4, H - 4, outline=lc, width=2)
        c.create_line(W // 2, 4, W // 2, H - 4, fill=lc, width=1)
        c.create_oval(W // 2 - 45, H // 2 - 45, W // 2 + 45, H // 2 + 45, outline=lc, width=1)
        c.create_oval(W // 2 - 4, H // 2 - 4, W // 2 + 4, H // 2 + 4, fill=lc)
        # Penalty areas
        c.create_rectangle(4, H // 2 - 60, 72, H // 2 + 60, outline=lc, width=1)
        c.create_rectangle(W - 72, H // 2 - 60, W - 4, H // 2 + 60, outline=lc, width=1)
        # Goal areas
        c.create_rectangle(4, H // 2 - 30, 30, H // 2 + 30, outline=lc, width=1)
        c.create_rectangle(W - 30, H // 2 - 30, W - 4, H // 2 + 30, outline=lc, width=1)
        # Goals
        c.create_rectangle(0, H // 2 - 20, 5, H // 2 + 20, fill="#BBBBBB", outline="")
        c.create_rectangle(W - 5, H // 2 - 20, W, H // 2 + 20, fill="#BBBBBB", outline="")
        # Penalty spots
        c.create_oval(52, H // 2 - 3, 58, H // 2 + 3, fill=lc)
        c.create_oval(W - 58, H // 2 - 3, W - 52, H // 2 + 3, fill=lc)
        # Corner arcs
        for cx, cy in [(5, 5), (W - 5, 5), (5, H - 5), (W - 5, H - 5)]:
            c.create_arc(cx - 12, cy - 12, cx + 12, cy + 12, start=0, extent=90, outline=lc, width=1)

    def animate_ball(self, event: str):
        W, H = PW, PH
        ev = event.upper()
        if "GOAL" in ev and "DISALLOWED" not in ev:
            x = random.choice([18, W - 18])
            y = H // 2 + random.randint(-18, 18)
        elif any(k in ev for k in ["SHOT", "STRIKE", "HEADER", "FREE KICK", "BIG CHANCE"]):
            x = random.randint(W // 2, W - 35) if random.random() < 0.5 else random.randint(35, W // 2)
            y = random.randint(28, H - 28)
        elif "FOUL" in ev or "CORNER" in ev or "CARD" in ev:
            x = random.choice([50, W - 50])
            y = random.choice([45, H - 45])
        elif "SUB" in ev:
            return
        elif "🌀" in event or "🔑" in event:
            x = random.randint(W // 3, 2 * W // 3)
            y = random.randint(H // 4, 3 * H // 4)
        else:
            x = random.randint(W // 4, 3 * W // 4)
            y = random.randint(H // 4, 3 * H // 4)
        self.coords(self.ball, x - 6, y - 6, x + 6, y + 6)
