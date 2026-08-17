import customtkinter as ctk

import app.state as state
from app.config import save_config
from app.constants import C_ACCENT, C_ACCENTL, C_CARD2, C_MUTED, C_TEXT, C_BORDER, OVERLAY_HTTP_PORT
from app.widgets import make_help
from app.tabs.features.gift_leaderboard_section import _make_color_btn


class TopLikeSection(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Tracks total likes sent per viewer and displays a live\n"
                 "leaderboard in the overlay � updates in real-time as likes arrive.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=C_MUTED,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(8, 10))

        # -- URL row
        url_row = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        url_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(
            url_row,
            text=f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/top-like",
            font=ctk.CTkFont("Consolas", 10),
            text_color=C_TEXT,
        ).pack(side="left", padx=(12, 4), pady=8)
        make_help(
            url_row,
            "Add this URL as a Link Source in TikTok LIVE Studio\nto display the Top Likers overlay.",
        ).pack(side="left", padx=(0, 4), pady=8)
        self._copy_btn = ctk.CTkButton(
            url_row, text="Copy URL", width=90, height=26,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._copy_url,
        )
        self._copy_btn.pack(side="right", padx=8, pady=6)

        # -- Overlay settings card
        cfg = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        cfg.pack(fill="x", padx=10, pady=(0, 12))
        cfg.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cfg, text="Overlay Settings",
            font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C_TEXT,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        self._username_color_var = ctk.StringVar()

        ctk.CTkLabel(
            cfg, text="Username Color", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=4)
        saved = state.config.get("top_like_username_color", "#ffffff")
        _make_color_btn(cfg, saved, self._username_color_var).grid(
            row=1, column=1, sticky="w", padx=(0, 12), pady=4,
        )

        ctk.CTkButton(
            cfg, text="Save Settings", height=32, corner_radius=8,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_settings,
        ).grid(row=2, column=0, columnspan=2, sticky="e", padx=12, pady=(6, 10))

    def _save_settings(self):
        state.config["top_like_username_color"] = self._username_color_var.get()
        save_config()
        from app.features.top_like import broadcast_leaderboard
        broadcast_leaderboard()

    def _copy_url(self):
        url = f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/top-like"
        self.clipboard_clear()
        self.clipboard_append(url)
        self._copy_btn.configure(text="Copied!")
        self.after(1500, lambda: self._copy_btn.configure(text="Copy URL"))
