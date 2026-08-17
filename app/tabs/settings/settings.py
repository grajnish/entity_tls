import customtkinter as ctk
from tkinter import filedialog

import app.state as state
from app.config import save_config
from app.constants import C_CARD, C_CARD2, C_ACCENT, C_ACCENTL, C_MUTED, C_BORDER
from app.widgets import make_card, make_label


class SettingsPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._vars = {}
        self._build()

    def _build(self):
        make_label(self, "Settings", 15, bold=True).pack(anchor="w", pady=(0, 14))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, pady=(0, 12))

        self._section(scroll, "🎵  TikTok LIVE", [
            ("username", "Username", "@meymeychang", False),
        ])

        self._folder_section(scroll)

        ctk.CTkButton(
            self, text="💾  Save Settings", height=42, corner_radius=12,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 13, "bold"),
            command=self._save
        ).pack(fill="x")

    def _folder_section(self, parent):
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 14))
        make_label(card, "🎶  Music Command (!play)", 12, bold=True, color="#a29bfe").pack(
            anchor="w", padx=16, pady=(14, 4)
        )
        ctk.CTkFrame(card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))
        make_label(
            card,
            "Folder containing music/video files. Viewers type  !play artist - song  in chat to queue a file.",
            10, color=C_MUTED,
        ).pack(anchor="w", padx=16, pady=(0, 6))

        row = ctk.CTkFrame(card, fg_color="transparent")
        row.pack(fill="x", padx=14, pady=(0, 12))
        make_label(row, "Music Folder", 12, color=C_MUTED).pack(side="left", padx=(0, 10), ipadx=24)
        var = ctk.StringVar(value=str(state.config.get("music_folder", "")))
        self._vars["music_folder"] = var
        ctk.CTkEntry(
            row, textvariable=var,
            placeholder_text="Select folder…",
            fg_color=C_CARD2, border_color=C_BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))
        ctk.CTkButton(
            row, text="Browse", width=80, height=28,
            fg_color=C_BORDER, hover_color="#2a2a50",
            font=ctk.CTkFont("Segoe UI", 11),
            command=lambda: var.set(filedialog.askdirectory(title="Select Music Folder") or var.get()),
        ).pack(side="left")

    def _section(self, parent, title, fields):
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 14))

        make_label(card, title, 12, bold=True, color="#a29bfe").pack(anchor="w", padx=16, pady=(14, 4))
        ctk.CTkFrame(card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))

        for key, label, placeholder, secret in fields:
            row = ctk.CTkFrame(card, fg_color="transparent")
            row.pack(fill="x", padx=14, pady=4)
            make_label(row, label, 12, color=C_MUTED).pack(side="left", padx=(0, 10), ipadx=60)

            var = ctk.StringVar(value=str(state.config.get(key, placeholder)))
            self._vars[key] = var

            ctk.CTkEntry(
                row, textvariable=var,
                show="●" if secret else "",
                placeholder_text=placeholder,
                fg_color=C_CARD2, border_color=C_BORDER,
            ).pack(side="left", fill="x", expand=True)

        ctk.CTkFrame(card, fg_color="transparent", height=8).pack()

    def _save(self):
        for key, var in self._vars.items():
            state.config[key] = var.get()
        save_config()
        self.app.log("Settings saved", "ok")
        self.app.pages["dashboard"].tt_user.configure(text=state.config.get("username", "—"))
