import customtkinter as ctk

import app.state as state
from app.constants import (
    TIER_KEYS, TIER_COLORS,
    C_ACCENTL, C_CARD2, C_GREEN, C_RED, C_TEXT, C_MUTED, C_BORDER,
)
from app.widgets import make_card, make_label, make_help


class JJVideoInfoPanel(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        self._build_stats()
        self._build_playbacks()

    def _build_stats(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))
        row.columnconfigure((0, 1, 2, 3), weight=1)

        stats = [
            ("QUEUE",       "queue_lbl",   "0",     C_TEXT,
             "Videos waiting to play.\nFills up when gifts arrive faster than videos finish."),
            ("NOW PLAYING", "playing_lbl", "IDLE",  C_MUTED,
             "Filename of the video currently showing in the overlay."),
            ("PLAYED",      "played_lbl",  "0",     C_ACCENTL,
             "Total videos played this session.\nResets when monitoring restarts."),
            ("STATUS",      "status_lbl",  "READY", C_GREEN,
             "ready   — idle, nothing queued\nplaying — video is active in overlay\nqueued  — video playing + more pending"),
        ]
        for col, (label, attr, default, color, tip) in enumerate(stats):
            card = make_card(row)
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            card_hdr = ctk.CTkFrame(card, fg_color="transparent")
            card_hdr.pack(fill="x", padx=8, pady=(8, 0))
            make_label(card_hdr, label, 8, color=C_MUTED).pack(side="left")
            make_help(card_hdr, tip).pack(side="right")
            lbl = make_label(card, default, 18, bold=True, color=color)
            lbl.pack(pady=(2, 10))
            setattr(self, attr, lbl)

    def _build_playbacks(self):
        card = make_card(self)
        card.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        make_label(hdr, "▶  Recent Playbacks", 12, bold=True, color=C_ACCENTL).pack(side="left")
        self._pb_clear_btn = ctk.CTkButton(
            hdr, text="Clear", width=54, height=22,
            fg_color="#1e1e40", hover_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._clear,
        )
        make_help(hdr, "Last 20 videos played this session, newest at top.\nTimestamp shows when each video started.\nClick Clear to reset the list.").pack(side="right", padx=(0, 6))

        self._pb_scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", corner_radius=0)
        self._pb_empty_lbl = make_label(card, "No recent playbacks", 11, color=C_MUTED)

        self._pb_items = []
        self.update_playbacks()

    def _clear(self):
        state._recent_playbacks.clear()
        self.update_playbacks()

    def update_playbacks(self):
        for w in self._pb_items:
            w.destroy()
        self._pb_items = []

        entries = list(state._recent_playbacks)
        if not entries:
            self._pb_scroll.pack_forget()
            self._pb_empty_lbl.pack(pady=20)
            self._pb_clear_btn.pack_forget()
            return

        self._pb_empty_lbl.pack_forget()
        self._pb_scroll.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        if not self._pb_clear_btn.winfo_ismapped():
            self._pb_clear_btn.pack(side="right")

        for ts, name in entries:
            row = ctk.CTkFrame(self._pb_scroll, fg_color=C_CARD2, corner_radius=6)
            row.pack(fill="x", pady=2)
            self._pb_items.append(row)
            make_label(row, ts, 9, color=C_MUTED).pack(side="left", padx=(8, 6), pady=5)
            short = (name[:28] + "…") if len(name) > 28 else name
            make_label(row, short, 11, color=C_TEXT).pack(side="left", fill="x", expand=True, padx=(0, 8))
