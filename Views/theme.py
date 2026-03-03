# Shared theme constants for all views
# Single source of truth — edit here to change the look app-wide
import os
from pathlib import Path

# Resolve absolute paths relative to this file so they work from any cwd
_HERE = Path(__file__).parent
LOGO_PNG = str(_HERE / "logo.png")
LOGO_ICO = str(_HERE / "logo.ico")
HOTEL_NAME = "Nona Lodge"

COLORS = {
    "bg":             "#111827",
    "sidebar":        "#1F2937",
    "card":           "#1F2937",
    "accent":         "#6366F1",
    "accent_hover":   "#4F46E5",
    "text_primary":   "#F9FAFB",
    "text_secondary": "#9CA3AF",
    "border":         "#374151",
    "success":        "#10B981",
    "danger":         "#EF4444",
    "warning":        "#F59E0B",
    "info":           "#3B82F6",
    "money_bg":       "#FFFFFF",
    "money_fg":       "#000000",
}

FONTS = {
    "logo":    ("Segoe UI", 20, "bold"),
    "title":   ("Segoe UI", 24, "bold"),
    "heading": ("Segoe UI", 16, "bold"),
    "label":   ("Segoe UI", 10, "bold"),
    "body":    ("Segoe UI", 11),
    "small":   ("Segoe UI", 9, "bold"),
    "badge":   ("Segoe UI", 8, "bold"),
    "btn":     ("Segoe UI", 12, "bold"),
    "topbar":  ("Segoe UI", 18, "bold"),
}
