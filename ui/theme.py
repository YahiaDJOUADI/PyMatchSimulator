import customtkinter as ctk

BACKGROUND      = "#05050E"
SIDEBAR_BG      = "#08081A"
CARD_BG         = "#0E0E1E"
CARD_HOVER      = "#171728"
GLASS_BG        = "#111128CC"

ACCENT          = "#D4AF37"
ACCENT_DARK     = "#A8892A"
ACCENT_LIGHT    = "#F0D060"
ACCENT_SECONDARY = "#8B8FA3"
EMERALD         = "#10B981"
EMERALD_DARK    = "#059669"
ELECTRIC_BLUE   = "#3B82F6"
ELECTRIC_DARK   = "#2563EB"
PURPLE          = "#8B5CF6"
PURPLE_DARK     = "#7C3AED"
NEON_CYAN       = "#06B6D4"
ROSE            = "#FB7185"
ORANGE          = "#F97316"

TEXT_PRIMARY    = "#F2F2FF"
TEXT_SECONDARY  = "#6B7080"
TEXT_MUTED      = "#3D4050"
TEXT_ACCENT     = "#D4AF37"

SUCCESS         = "#00FF9D"
DANGER          = "#FF3366"
WARNING         = "#FFD700"
INFO            = "#60A5FA"

GLOW_GOLD       = "#D4AF3740"
GLOW_GREEN      = "#10B98140"
GLOW_BLUE       = "#3B82F640"
GLOW_CYAN       = "#06B6D440"

BORDER_COLOR    = "#1E1E30"
BORDER_ACCENT   = "#3D3110"
CORNER_RADIUS   = 12
CORNER_SMALL    = 8

GRADIENT_GOLD   = ("#D4AF37", "#A8892A")
GRADIENT_GREEN  = ("#10B981", "#059669")
GRADIENT_BLUE   = ("#3B82F6", "#2563EB")
GRADIENT_PURPLE = ("#8B5CF6", "#7C3AED")
GRADIENT_CYAN   = ("#06B6D4", "#0891B2")

ROW_EVEN        = "#0C0C1A"
ROW_ODD         = "#101022"
ROW_HOVER       = "#181830"


ANIM_FAST       = 150
ANIM_MED        = 300
ANIM_SLOW       = 500

def get_font(size: int = 14, weight: str = "normal") -> ctk.CTkFont:
    return ctk.CTkFont(family="Segoe UI", size=size, weight=weight)

def get_mono_font(size: int = 12) -> ctk.CTkFont:
    return ctk.CTkFont(family="Consolas", size=size)

FONT_TITLE   = lambda: get_font(28, "bold")
FONT_HEADING = lambda: get_font(20, "bold")
FONT_BODY    = lambda: get_font(14)
FONT_CAPTION = lambda: get_font(11)
FONT_SMALL   = lambda: get_font(10)
FONT_TINY    = lambda: get_font(9)


def setup_theme():
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")


def rating_color(rating: int) -> str:
    return "#FFD700" if rating >= 90 else ("#C0C0C0" if rating >= 85 else ("#CD7F32" if rating >= 80 else (EMERALD if rating >= 75 else TEXT_SECONDARY)))


def form_color(form: float) -> str:
    return SUCCESS if form >= 1.1 else (EMERALD if form >= 1.0 else (WARNING if form >= 0.9 else DANGER))


def morale_color(morale: float) -> str:
    return SUCCESS if morale >= 1.3 else (EMERALD if morale >= 1.0 else (WARNING if morale >= 0.8 else DANGER))

def create_icon_image(icon_code: str, size: int = 20, color: str = TEXT_SECONDARY) -> ctk.CTkImage:
    import os
    from PIL import Image, ImageDraw, ImageFont
    
    font_path = os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "MaterialIcons-Regular.ttf")
    if not os.path.exists(font_path):
        return None
        
    try:
        font = ImageFont.truetype(font_path, size)
    except Exception:
        return None
        
    img = Image.new("RGBA", (size + 4, size + 4), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    
    try:
        bbox = d.textbbox((0, 0), icon_code, font=font)
        w = bbox[2] - bbox[0]
        h = bbox[3] - bbox[1]
        x = (size + 4 - w) / 2
        y = (size + 4 - h) / 2 - 2
    except AttributeError:
        # Fallback for older Pillow versions
        w, h = d.textsize(icon_code, font=font)
        x = (size + 4 - w) / 2
        y = (size + 4 - h) / 2 - 2

    d.text((x, y), icon_code, font=font, fill=color)
    return ctk.CTkImage(light_image=img, dark_image=img, size=(size, size))
