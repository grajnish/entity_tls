# -*- coding: utf-8 -*-
from tkinter import filedialog

import customtkinter as ctk

import app.state as state
from app.config import save_config
from app.constants import (
    C_CARD, C_CARD2, C_ACCENT, C_ACCENTL, C_MUTED, C_BORDER, C_TEXT, C_RED,
    OVERLAY_HTTP_PORT,
)
from app.widgets import make_help


class JJVideoSection(ctk.CTkFrame):
    """Auto-play a random video from each tier pool when gifts are received."""

    _BUILTIN_KEYS = ["10", "20", "30", "100", "200", "300", "500", "1000", "2000"]
    _BUILTIN_COLORS = {
        "10": "#1a5c38", "20": "#14506a", "30": "#4a2370",
        "100": "#1a5c38", "200": "#14506a", "300": "#4a2370",
        "500": "#7a2218", "1000": "#6b5607", "2000": "#1a252f",
    }
    _CUSTOM_PALETTE = [
        "#2d1b69", "#0d3b2e", "#3d1515", "#0f2a3d",
        "#2a0a2e", "#1e3a1e", "#3d2800", "#0a2a3d",
    ]

    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._tier_frames = {}   # key -> (card, videos_frame)
        self._tier_vars = {}     # key -> [StringVar, ...]
        self._custom_color_idx = 0
        self._custom_coin_var = ctk.StringVar()
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Plays a random video from the assigned pool when a gift is received.\n"
                 "Each tier can hold multiple videos - one is picked at random each time.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=C_MUTED,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(8, 10))

        # Overlay URL bar
        url_row = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        url_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(
            url_row,
            text=f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/jj-video",
            font=ctk.CTkFont("Consolas", 10),
            text_color=C_TEXT,
        ).pack(side="left", padx=(12, 4), pady=8)
        make_help(
            url_row,
            "Add this URL as a Link Source in TikTok LIVE Studio\nto display the JJ Video overlay.",
        ).pack(side="left", padx=(0, 4), pady=8)
        self._copy_btn = ctk.CTkButton(
            url_row, text="Copy URL", width=90, height=26,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._copy_url,
        )
        self._copy_btn.pack(side="right", padx=8, pady=6)

        # Section header
        ctk.CTkFrame(self, fg_color=C_BORDER, height=1).pack(fill="x", padx=10, pady=(2, 6))
        ctk.CTkLabel(
            self, text="Tier to Video Mapping",
            font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C_MUTED, anchor="w",
        ).pack(anchor="w", padx=12, pady=(0, 6))

        # Scrollable tier cards
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=10, pady=(0, 4))
        self._tiers_container = scroll

        self._add_tier_card("default", is_custom=False)
        for key in self._BUILTIN_KEYS:
            self._add_tier_card(key, is_custom=False)

        # Restore custom tiers from saved config
        saved_tiers = state.config.get("tiers", {})
        for key in sorted(saved_tiers, key=lambda k: int(k) if k.isdigit() else -1):
            if key.isdigit() and key not in self._BUILTIN_KEYS:
                self._add_tier_card(key, is_custom=True)

        # Add custom tier row
        add_row = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        add_row.pack(fill="x", padx=10, pady=(2, 4))
        ctk.CTkLabel(
            add_row, text="Add Custom Tier:",
            font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C_TEXT,
        ).pack(side="left", padx=(12, 8), pady=8)
        ctk.CTkEntry(
            add_row, textvariable=self._custom_coin_var,
            width=80, height=28, placeholder_text="e.g. 3000",
            font=ctk.CTkFont("Consolas", 11),
            fg_color=C_CARD, border_color=C_BORDER,
        ).pack(side="left", padx=(0, 4), pady=8)
        ctk.CTkLabel(
            add_row, text="coins", text_color=C_MUTED,
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(side="left", padx=(0, 12), pady=8)
        ctk.CTkButton(
            add_row, text="+ Add Tier", width=100, height=28,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._add_custom_tier,
        ).pack(side="left", pady=8)

        # Save button
        ctk.CTkButton(
            self, text="Save", height=36, corner_radius=10,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 12, "bold"),
            command=self._save,
        ).pack(fill="x", padx=12, pady=(4, 12))

    # -- Tier card -------------------------------------------------------------

    def _add_tier_card(self, key, is_custom=False):
        if key == "default":
            badge_color = C_MUTED
            badge_text  = "DEFAULT"
            existing    = _as_list(state.config.get("default_video", []))
        elif key in self._BUILTIN_COLORS:
            badge_color = self._BUILTIN_COLORS[key]
            badge_text  = f"{key}c"
            existing    = _as_list(state.config.get("tiers", {}).get(key, []))
        else:
            badge_color = self._CUSTOM_PALETTE[self._custom_color_idx % len(self._CUSTOM_PALETTE)]
            self._custom_color_idx += 1
            badge_text  = f"{key}c"
            existing    = _as_list(state.config.get("tiers", {}).get(key, []))

        card = ctk.CTkFrame(self._tiers_container, fg_color=C_CARD2, corner_radius=8)
        card.pack(fill="x", pady=(0, 6))

        # videos_frame must exist before hdr button lambda captures it
        videos_frame = ctk.CTkFrame(card, fg_color="transparent")

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=8, pady=(8, 4))

        ctk.CTkLabel(
            hdr, text=badge_text, width=72,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            fg_color=badge_color, corner_radius=6, text_color="white",
        ).pack(side="left", padx=(0, 8))

        if is_custom:
            ctk.CTkButton(
                hdr, text="Remove", width=76, height=24,
                fg_color="#3d1515", hover_color=C_RED,
                font=ctk.CTkFont("Segoe UI", 10),
                command=lambda c=card, k=key: self._delete_tier(c, k),
            ).pack(side="right", padx=(4, 0))

        ctk.CTkButton(
            hdr, text="+ Video", width=72, height=24,
            fg_color=C_BORDER, hover_color="#2a2a50",
            font=ctk.CTkFont("Segoe UI", 10),
            command=lambda k=key, vf=videos_frame: self._add_video_row(k, vf),
        ).pack(side="right", padx=(0, 4))

        videos_frame.pack(fill="x", padx=8, pady=(0, 8))

        self._tier_frames[key] = (card, videos_frame)
        self._tier_vars[key] = []

        for path in (existing if existing else [""]):
            self._add_video_row(key, videos_frame, path)

    def _add_video_row(self, key, videos_frame, path=""):
        row = ctk.CTkFrame(videos_frame, fg_color="transparent")
        row.pack(fill="x", pady=2)

        var = ctk.StringVar(value=path)
        self._tier_vars.setdefault(key, []).append(var)

        ctk.CTkEntry(
            row, textvariable=var,
            font=ctk.CTkFont("Consolas", 10),
            placeholder_text="No file selected - click Browse",
            fg_color=C_CARD, border_color=C_BORDER,
        ).pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            row, text="Browse", width=70, height=28,
            fg_color=C_BORDER, hover_color="#2a2a50",
            font=ctk.CTkFont("Segoe UI", 11),
            command=lambda v=var: self._browse(v),
        ).pack(side="left", padx=(0, 4))

        def _remove(r=row, k=key, v=var):
            if v in self._tier_vars.get(k, []):
                self._tier_vars[k].remove(v)
            r.destroy()

        ctk.CTkButton(
            row, text="X", width=28, height=28,
            fg_color="#3d1515", hover_color=C_RED,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=_remove,
        ).pack(side="left")

    # -- Actions ---------------------------------------------------------------

    def _add_custom_tier(self):
        raw = self._custom_coin_var.get().strip()
        if not raw.isdigit() or int(raw) <= 0:
            self.app.log("Enter a valid positive coin number", "warn")
            return
        key = str(int(raw))  # strip leading zeros
        if key in self._tier_vars:
            self.app.log(f"Tier {key}c already exists", "warn")
            return
        self._add_tier_card(key, is_custom=True)
        self._custom_coin_var.set("")

    def _delete_tier(self, card, key):
        card.destroy()
        self._tier_frames.pop(key, None)
        self._tier_vars.pop(key, None)

    def _browse(self, var):
        path = filedialog.askopenfilename(
            title="Select video file",
            filetypes=[
                ("Video files", "*.mp4 *.MP4 *.mov *.MOV *.webm *.WEBM *.avi *.AVI"),
                ("All files", "*.*"),
            ],
        )
        if path:
            var.set(path)

    def _save(self):
        tiers = {}
        for key, vars_list in self._tier_vars.items():
            paths = [v.get() for v in vars_list if v.get().strip()]
            if key == "default":
                state.config["default_video"] = paths
            else:
                tiers[key] = paths
        state.config["tiers"] = tiers
        save_config()
        self.app.log("JJ Video tiers saved", "ok")

    def _copy_url(self):
        url = f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/jj-video"
        self.clipboard_clear()
        self.clipboard_append(url)
        self._copy_btn.configure(text="Copied!")
        self.after(1500, lambda: self._copy_btn.configure(text="Copy URL"))


def _as_list(v):
    """Normalize a legacy single-string or new list tier value to a list."""
    if isinstance(v, list):
        return [p for p in v if p]
    return [v] if v else []
