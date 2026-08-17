import datetime
import sys
import tkinter as tk
from pathlib import Path

import customtkinter as ctk

from app.constants import C_CARD, C_CARD2, C_BORDER, C_MUTED, C_TEXT, LOG_COLORS


def set_icon(window):
    """Apply entity-icon.ico to any Tk/CTkToplevel window."""
    base = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parent.parent
    ico = base / "entity-icon.ico"
    if ico.exists():
        window.after(0, lambda: window.iconbitmap(str(ico)))


def make_card(parent, **kwargs):
    return ctk.CTkFrame(parent, fg_color=C_CARD, corner_radius=14, **kwargs)


def make_label(parent, text, size=12, bold=False, color=C_TEXT, **kwargs):
    return ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont("Segoe UI", size, "bold" if bold else "normal"),
        text_color=color, **kwargs
    )


def make_logbox(parent):
    box = ctk.CTkTextbox(
        parent, state="disabled",
        font=ctk.CTkFont("Consolas", 11),
        fg_color=C_CARD2, corner_radius=10,
        text_color=C_TEXT,
    )
    for tag, color in LOG_COLORS.items():
        box._textbox.tag_config(tag, foreground=color)
    return box


def write_log(box, message, tag="info"):
    ts = datetime.datetime.now().strftime("%H:%M:%S")
    box.configure(state="normal")
    box._textbox.insert("end", f"[{ts}]  {message}\n", tag)
    box._textbox.see("end")
    box.configure(state="disabled")


class _Tooltip:
    """Borderless hover tooltip."""
    def __init__(self, widget, text):
        self._widget = widget
        self._text   = text
        self._win    = None
        widget.bind("<Enter>", self._show, add="+")
        widget.bind("<Leave>", self._hide, add="+")

    def _show(self, _event):
        if self._win:
            return
        x = self._widget.winfo_rootx() + 24
        y = self._widget.winfo_rooty() + 20
        self._win = tk.Toplevel(self._widget)
        self._win.wm_overrideredirect(True)
        self._win.wm_geometry(f"+{x}+{y}")
        self._win.configure(bg=C_BORDER)
        tk.Label(
            self._win, text=self._text,
            bg=C_CARD, fg=C_TEXT,
            font=("Segoe UI", 9),
            justify="left",
            wraplength=240,
            padx=10, pady=7,
        ).pack(padx=1, pady=1)

    def _hide(self, _event):
        if self._win:
            self._win.destroy()
            self._win = None


def make_help(parent, text):
    lbl = ctk.CTkLabel(
        parent, text="?", width=16, height=16,
        fg_color=C_BORDER, corner_radius=8,
        font=ctk.CTkFont("Segoe UI", 8, "bold"),
        text_color=C_MUTED, cursor="question_arrow",
    )
    _Tooltip(lbl, text)
    return lbl
