"""Shared visual language and small layout helpers for the desktop UI."""

import customtkinter as ctk


COLORS = {
    "app_bg": "#111318",
    "sidebar": "#171A21",
    "surface": "#1B1F27",
    "surface_alt": "#20252F",
    "surface_hover": "#292F3A",
    "input": "#14171D",
    "border": "#303744",
    "text": "#F2F5F9",
    "muted": "#9AA4B2",
    "accent": "#3B82F6",
    "accent_hover": "#2563EB",
    "success": "#22A06B",
    "success_hover": "#1A7F55",
    "danger": "#D84A4A",
    "danger_hover": "#B83C3C",
    "cyan": "#1595B6",
    "warning": "#E6A23C",
}

PAGE_PAD = 18
CARD_RADIUS = 14


def page_header(parent, app, title, subtitle):
    """Create a compact page title with supporting text."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x", padx=PAGE_PAD, pady=(16, 8))
    ctk.CTkLabel(
        frame,
        text=title,
        font=app.title_font,
        text_color=COLORS["text"],
    ).pack(anchor="w")
    ctk.CTkLabel(
        frame,
        text=subtitle,
        font=app.small_font,
        text_color=COLORS["muted"],
    ).pack(anchor="w", pady=(2, 0))
    return frame


def card(parent, **kwargs):
    """Create a standard surface card."""
    options = {
        "fg_color": COLORS["surface"],
        "corner_radius": CARD_RADIUS,
        "border_width": 1,
        "border_color": COLORS["border"],
    }
    options.update(kwargs)
    return ctk.CTkFrame(parent, **options)


def section_heading(parent, app, title, subtitle=None):
    """Create a reusable section heading inside a card."""
    frame = ctk.CTkFrame(parent, fg_color="transparent")
    frame.pack(fill="x")
    ctk.CTkLabel(
        frame, text=title, font=app.section_font, text_color=COLORS["text"]
    ).pack(anchor="w")
    if subtitle:
        ctk.CTkLabel(
            frame,
            text=subtitle,
            font=app.small_font,
            text_color=COLORS["muted"],
        ).pack(anchor="w", pady=(2, 0))
    return frame


def muted_label(parent, app, text, **kwargs):
    options = {
        "text": text,
        "font": app.small_font,
        "text_color": COLORS["muted"],
    }
    options.update(kwargs)
    return ctk.CTkLabel(parent, **options)
