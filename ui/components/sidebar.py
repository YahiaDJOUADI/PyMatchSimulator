import os
import customtkinter as ctk
from PIL import Image
from ui.theme import (SIDEBAR_BG, ACCENT, ACCENT_LIGHT, TEXT_PRIMARY, get_font, BORDER_COLOR,
                      TEXT_SECONDARY, CARD_BG, CARD_HOVER, EMERALD, NEON_CYAN, ANIM_FAST, create_icon_image)

NAV_ITEMS = [
    ("dashboard",       "\ue88a", "Dashboard"),
    ("match",           "\uea2f", "Play Match"),
    ("team_manager",    "\ue7ef", "Teams"),
    ("league_table",    "\ue0ee", "League"),
    ("season",          "\ue878", "Season"),
    ("tournament",      "\uea23", "Cup"),
    ("transfer_market", "\ue8d4", "Transfers"),
    ("match_history",   "\ue889", "History"),
    ("rankings",        "\ue838", "Rankings"),
    ("awards",          "\uea3f", "Awards"),
]

SECTION_BREAKS = {"transfer_market", "match_history"}


class Sidebar(ctk.CTkFrame):
    def __init__(self, master, on_change_view, **kwargs):
        super().__init__(master, fg_color=SIDEBAR_BG, width=225, corner_radius=0,
                         border_width=1, border_color=BORDER_COLOR)
        self.on_change_view = on_change_view
        self.buttons: dict[str, tuple] = {}
        self.active_view = None
        self._build()

    def _build(self):
        brand = ctk.CTkFrame(self, fg_color="transparent")
        brand.pack(pady=(22, 4), padx=12)

        logo_frame = ctk.CTkFrame(brand, fg_color="transparent", width=80, height=80)
        logo_frame.pack()
        logo_frame.pack_propagate(False)
        
        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            img = Image.open(logo_path)
            logo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(80, 80))
            ctk.CTkLabel(logo_frame, text="", image=logo_img).place(relx=0.5, rely=0.5, anchor="center")
        else:
            ctk.CTkLabel(logo_frame, text="⚽", font=get_font(40)).place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(brand, text="PyMatch", font=get_font(18, "bold"),
                     text_color=ACCENT).pack(pady=(6, 0))
        ctk.CTkLabel(brand, text="SIMULATOR", font=get_font(8, "bold"),
                     text_color=TEXT_SECONDARY).pack()

        ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=14, pady=14)
        ctk.CTkLabel(self, text="NAVIGATE", font=get_font(8, "bold"),
                     text_color=TEXT_SECONDARY).pack(anchor="w", padx=18, pady=(0, 4))

        for view_id, icon, label in NAV_ITEMS:
            if view_id in SECTION_BREAKS:
                ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR).pack(fill="x", padx=14, pady=6)
            self._make_btn(view_id, icon, label)

        ctk.CTkFrame(self, height=1, fg_color=BORDER_COLOR).pack(
            fill="x", padx=14, pady=(14, 0), side="bottom"
        )
        ctk.CTkLabel(self, text="Ultra Premium Edition", font=get_font(8),
                     text_color=TEXT_SECONDARY).pack(side="bottom", pady=8)

    def _make_btn(self, view_id: str, icon_code: str, label: str):
        container = ctk.CTkFrame(self, fg_color="transparent", height=40, corner_radius=8)
        container.pack(fill="x", padx=8, pady=2)
        container.pack_propagate(False)

        stripe = ctk.CTkFrame(container, width=4, height=26, fg_color="transparent", corner_radius=2)
        stripe.pack(side="left", padx=(4, 0), pady=7)

        img_inactive = create_icon_image(icon_code, size=20, color=TEXT_SECONDARY)
        img_active = create_icon_image(icon_code, size=20, color=TEXT_PRIMARY)

        btn = ctk.CTkButton(
            container,
            text=f"  {label}",
            image=img_inactive if img_inactive else None,
            anchor="w",
            font=get_font(12),
            fg_color="transparent",
            hover_color=CARD_HOVER,
            text_color=TEXT_SECONDARY,
            corner_radius=6,
            height=34,
            command=lambda v=view_id: self.on_change_view(v),
        )
        btn.pack(side="left", fill="both", expand=True, padx=(2, 4))

        btn.bind("<Enter>", lambda e, c=container: c.configure(fg_color="#111122"))
        btn.bind("<Leave>", lambda e, c=container, v=view_id: (
            None if self.active_view == v else c.configure(fg_color="transparent")
        ))

        self.buttons[view_id] = (container, btn, stripe, img_inactive, img_active)

    def set_active(self, view_id: str):
        for vid, (container, btn, stripe, img_inactive, img_active) in self.buttons.items():
            container.configure(fg_color="transparent")
            if img_inactive:
                btn.configure(text_color=TEXT_SECONDARY, font=get_font(12), image=img_inactive)
            else:
                btn.configure(text_color=TEXT_SECONDARY, font=get_font(12))
            stripe.configure(fg_color="transparent")

        if view_id in self.buttons:
            container, btn, stripe, img_inactive, img_active = self.buttons[view_id]
            container.configure(fg_color=CARD_HOVER)
            if img_active:
                btn.configure(text_color=TEXT_PRIMARY, font=get_font(12, "bold"), image=img_active)
            else:
                btn.configure(text_color=TEXT_PRIMARY, font=get_font(12, "bold"))
            stripe.configure(fg_color=ACCENT)

        self.active_view = view_id
