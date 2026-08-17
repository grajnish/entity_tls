import customtkinter as ctk

import app.state as state
from app.constants import C_ACCENT, C_ACCENTL, C_CARD2, C_MUTED, C_RED, C_TEXT
from app.widgets import make_card, make_label, make_help


class MusicPlayerPanel(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        self._build_stats()
        self._build_controls()
        self._build_queue()

    # ── Stats row ─────────────────────────────────────────────────────────
    def _build_stats(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))
        row.columnconfigure((0, 1, 2), weight=1)

        defs = [
            ("NOW PLAYING",  "np_lbl",   "—", C_TEXT,
             "Title of the track currently playing in the overlay."),
            ("REQUESTED BY", "req_lbl",  "—", C_MUTED,
             "Username who requested the current track."),
            ("QUEUE",        "qlen_lbl", "0", C_ACCENTL,
             "Songs waiting to be played."),
        ]
        for col, (label, attr, default, color, tip) in enumerate(defs):
            card = make_card(row)
            card.grid(row=0, column=col, sticky="nsew", padx=4)
            hdr = ctk.CTkFrame(card, fg_color="transparent")
            hdr.pack(fill="x", padx=8, pady=(8, 0))
            make_label(hdr, label, 8, color=C_MUTED).pack(side="left")
            make_help(hdr, tip).pack(side="right")
            lbl = make_label(card, default, 14, bold=True, color=color)
            lbl.pack(pady=(2, 10))
            setattr(self, attr, lbl)

    # ── Playback controls card ─────────────────────────────────────────────
    def _build_controls(self):
        card = make_card(self)
        card.pack(fill="x", pady=(0, 8))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        make_label(hdr, "PLAYBACK CONTROLS", 11, bold=True, color=C_ACCENTL).pack(side="left")

        pb_row = ctk.CTkFrame(card, fg_color="transparent")
        pb_row.pack(fill="x", padx=14, pady=(0, 6))
        ctk.CTkButton(
            pb_row, text="\u23f8  Pause", height=32, width=100, corner_radius=8,
            fg_color="#333355", hover_color="#444477",
            font=ctk.CTkFont("Segoe UI", 11), command=self._pause,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            pb_row, text="\u25b6  Resume", height=32, width=100, corner_radius=8,
            fg_color="#1a3a1a", hover_color="#2a5a2a",
            font=ctk.CTkFont("Segoe UI", 11), command=self._resume,
        ).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            pb_row, text="\u23ed  Skip", height=32, width=80, corner_radius=8,
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            font=ctk.CTkFont("Segoe UI", 11), command=self._skip_track,
        ).pack(side="left")

        vol_row = ctk.CTkFrame(card, fg_color="transparent")
        vol_row.pack(fill="x", padx=14, pady=(0, 10))
        make_label(vol_row, "Volume", 11, color=C_MUTED).pack(side="left", padx=(0, 6))
        ctk.CTkButton(
            vol_row, text="\u2212", width=28, height=28, corner_radius=6,
            fg_color=C_CARD2, hover_color="#333344",
            font=ctk.CTkFont("Segoe UI", 13, "bold"), command=self._vol_down,
        ).pack(side="left", padx=(0, 4))
        init_vol = int(state.music_volume * 100)
        self._vol_slider = ctk.CTkSlider(
            vol_row, from_=0, to=100, width=160,
            command=self._on_vol_change,
        )
        self._vol_slider.set(init_vol)
        self._vol_slider.pack(side="left", padx=(0, 4))
        ctk.CTkButton(
            vol_row, text="+", width=28, height=28, corner_radius=6,
            fg_color=C_CARD2, hover_color="#333344",
            font=ctk.CTkFont("Segoe UI", 13, "bold"), command=self._vol_up,
        ).pack(side="left", padx=(0, 8))
        self._vol_label = make_label(vol_row, f"{init_vol}%", 11, color=C_MUTED)
        self._vol_label.pack(side="left")

    # ── Queue card ─────────────────────────────────────────────────────────
    def _build_queue(self):
        card = make_card(self)
        card.pack(fill="x", pady=(0, 8))

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        make_label(hdr, "NOW PLAYING & QUEUE", 11, bold=True, color=C_ACCENTL).pack(side="left")
        ctk.CTkButton(
            hdr, text="\u21ba", width=28, height=24, corner_radius=6,
            fg_color=C_CARD2, hover_color="#333344",
            font=ctk.CTkFont("Segoe UI", 11), command=self._refresh_queue,
        ).pack(side="right")
        ctk.CTkButton(
            hdr, text="\U0001f5d1  Clear All", width=80, height=24, corner_radius=6,
            fg_color="#3a1a1a", hover_color="#5a2a2a",
            font=ctk.CTkFont("Segoe UI", 10), command=self._clear_queue,
        ).pack(side="right", padx=(0, 4))

        self._queue_frame = ctk.CTkFrame(card, fg_color="transparent")
        self._queue_frame.pack(fill="x", padx=14, pady=(0, 10))
        self._poll_queue()

    # ── Handlers ──────────────────────────────────────────────────────────
    def _skip_track(self):
        import app.features.comment_player as cp
        cp._on_track_ended()
        self.app.log("[Music] Track skipped.", "info")

    def _stop_current(self):
        import app.features.comment_player as cp
        cp.stop_current()
        self.app.log("[Music] Now playing stopped.", "info")
        self._refresh_queue()

    def _clear_queue(self):
        import app.features.comment_player as cp
        cp.clear_all()
        self.app.log("[Music] Queue and now playing cleared.", "info")
        self._refresh_queue()

    def _remove_queue_item(self, index: int):
        import app.features.comment_player as cp
        cp.remove_queue_item(index)
        self.app.log(f"[Music] Removed queue item #{index + 1}.", "info")
        self._refresh_queue()

    def _pause(self):
        state.music_paused = True
        import app.features.comment_player as cp
        cp.send_control("pause")

    def _resume(self):
        state.music_paused = False
        import app.features.comment_player as cp
        cp.send_control("resume")

    def _on_vol_change(self, val):
        vol = round(float(val) / 100, 2)
        state.music_volume = vol
        self._vol_label.configure(text=f"{int(float(val))}%")
        import app.features.comment_player as cp
        cp.send_control("set_volume", value=vol)

    def _vol_down(self):
        v = max(0, self._vol_slider.get() - 10)
        self._vol_slider.set(v)
        self._on_vol_change(v)

    def _vol_up(self):
        v = min(100, self._vol_slider.get() + 10)
        self._vol_slider.set(v)
        self._on_vol_change(v)

    def _refresh_queue(self):
        for w in self._queue_frame.winfo_children():
            w.destroy()
        cur = state.music_current

        if cur.get("status") == "playing":
            title = cur.get("title", "Unknown")
            short = (title[:22] + "\u2026") if len(title) > 22 else title
            self.np_lbl.configure(text=short, text_color="#00dcb4")
            self.req_lbl.configure(text=cur.get("requester", "\u2014"))
        else:
            self.np_lbl.configure(text="\u2014", text_color=C_TEXT)
            self.req_lbl.configure(text="\u2014")
        self.qlen_lbl.configure(text=str(len(state.music_display_queue)))

        if cur.get("status") == "playing":
            row = ctk.CTkFrame(self._queue_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            line = "\u25b6  " + cur.get("title", "Unknown")
            if cur.get("requester"):
                line += "  \u2022  " + cur["requester"]
            ctk.CTkLabel(
                row, text=line, anchor="w",
                font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color="#00dcb4",
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="\u2715", width=24, height=20, corner_radius=4,
                fg_color="#3a1a1a", hover_color="#5a2a2a",
                font=ctk.CTkFont("Segoe UI", 10), command=self._stop_current,
            ).pack(side="right")
        elif cur.get("status") == "searching":
            row = ctk.CTkFrame(self._queue_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row,
                text="\u231b  Searching: " + cur.get("title", ""),
                anchor="w", font=ctk.CTkFont("Segoe UI", 11), text_color="#ffcc44",
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="\u2715", width=24, height=20, corner_radius=4,
                fg_color="#3a1a1a", hover_color="#5a2a2a",
                font=ctk.CTkFont("Segoe UI", 10), command=self._stop_current,
            ).pack(side="right")
        else:
            ctk.CTkLabel(
                self._queue_frame, text="\u2014 Nothing playing \u2014", anchor="w",
                font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
            ).pack(fill="x", pady=1)

        for i, item in enumerate(state.music_display_queue):
            title  = item.get("_resolved_title") or item.get("query", "")
            req    = item.get("requester", "")
            suffix = " (searching\u2026)" if item.get("_preloading") and "info" not in item else ""
            line   = f"{i + 1}.  {title}{suffix}" + (f"  \u2022  {req}" if req else "")
            row = ctk.CTkFrame(self._queue_frame, fg_color="transparent")
            row.pack(fill="x", pady=1)
            ctk.CTkLabel(
                row, text=line, anchor="w",
                font=ctk.CTkFont("Segoe UI", 10), text_color=C_MUTED,
            ).pack(side="left", fill="x", expand=True)
            ctk.CTkButton(
                row, text="\u2715", width=24, height=20, corner_radius=4,
                fg_color="#2a1a2a", hover_color="#4a2a4a",
                font=ctk.CTkFont("Segoe UI", 10), command=lambda idx=i: self._remove_queue_item(idx),
            ).pack(side="right")

    def _poll_queue(self):
        self._refresh_queue()
        self.after(2000, self._poll_queue)
