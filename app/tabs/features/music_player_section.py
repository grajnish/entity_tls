import customtkinter as ctk

import app.state as state
from app.config import save_config
from app.constants import C_ACCENT, C_ACCENTL, C_CARD2, C_MUTED, C_TEXT, C_BORDER, OVERLAY_HTTP_PORT
from app.widgets import make_help


class MusicPlayerSection(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Viewers request songs by typing  !play <song title>  in chat.\n"
                 "The overlay shows the now-playing card + queue list with thumbnail,\n"
                 "title, artist and requester name.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=C_MUTED,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(8, 10))

        # ── Overlay URL row ───────────────────────────────────────────────
        url_row = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        url_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(
            url_row,
            text=f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/music-player",
            font=ctk.CTkFont("Consolas", 10),
            text_color=C_TEXT,
        ).pack(side="left", padx=(12, 4), pady=8)
        make_help(
            url_row,
            "Add this URL as a Link Source in TikTok LIVE Studio\n"
            "to display the Music Player overlay.\n"
            "Audio plays directly from the Link Source in TikTok LIVE Studio.",
        ).pack(side="left", padx=(0, 4), pady=8)
        self._copy_btn = ctk.CTkButton(
            url_row, text="Copy URL", width=90, height=26,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._copy_url,
        )
        self._copy_btn.pack(side="right", padx=8, pady=6)

        # ── Settings card ─────────────────────────────────────────────────
        cfg = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        cfg.pack(fill="x", padx=10, pady=(0, 12))
        cfg.columnconfigure(1, weight=1)

        ctk.CTkLabel(
            cfg, text="Settings",
            font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C_TEXT,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        ctk.CTkLabel(
            cfg, text="Max Queue Size", width=140, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=4)
        self._max_queue_var = ctk.StringVar(value=str(state.config.get("music_max_queue", 10)))
        ctk.CTkEntry(
            cfg, textvariable=self._max_queue_var,
            width=70, height=28, corner_radius=8,
            fg_color="#1e1e2e", border_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 11), justify="center",
        ).grid(row=1, column=1, sticky="w", padx=(0, 12), pady=4)

        ctk.CTkLabel(
            cfg, text="Min Coins to Request", width=140, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=2, column=0, sticky="w", padx=(12, 8), pady=4)
        self._min_coins_var = ctk.StringVar(value=str(state.config.get("music_min_coins", 0)))
        ctk.CTkEntry(
            cfg, textvariable=self._min_coins_var,
            width=70, height=28, corner_radius=8,
            fg_color="#1e1e2e", border_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 11), justify="center",
        ).grid(row=2, column=1, sticky="w", padx=(0, 12), pady=4)
        make_help(
            cfg,
            "Set to 0 to let everyone request.\n"
            "Set > 0 to require the viewer to have sent at least that\n"
            "many coins this session before they can !play.",
        ).grid(row=2, column=1, sticky="e", padx=(0, 12), pady=4)

        _color_rows = [
            ("Song Title Color",  "_song_color",   "music_color_song",        "#ffffff"),
            ("Artist Color",      "_artist_color", "music_color_artist",      "#b4ffeb"),
            ("Username Color",    "_user_color",   "music_color_user",        "#aaaaaa"),
            ("Queue Label Color", "_qlabel_color", "music_color_queue_label", "#00dcb4"),
            ("Queue Index Color", "_qindex_color", "music_color_queue_index", "#00dcb4"),
            ("Queue Song Color",  "_qsong_color",  "music_color_queue_song",  "#d9d9d9"),
            ("Queue By Color",    "_qby_color",    "music_color_queue_by",    "#595959"),
        ]
        for i, (label, attr, key, default) in enumerate(_color_rows, start=3):
            ctk.CTkLabel(
                cfg, text=label, width=140, anchor="w",
                font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
            ).grid(row=i, column=0, sticky="w", padx=(12, 8), pady=3)
            saved = state.config.get(key, default)
            var = ctk.StringVar(value=saved)
            setattr(self, f"{attr}_var", var)
            holder = [None]
            def _make_cmd(v, h):
                def _pick():
                    import tkinter.colorchooser as cc
                    result = cc.askcolor(color=v.get(), title="Pick color", parent=self)
                    if result[1]:
                        v.set(result[1])
                        h[0].configure(fg_color=result[1], hover_color=result[1])
                return _pick
            btn = ctk.CTkButton(
                cfg, text="", width=40, height=28, corner_radius=8,
                fg_color=saved, hover_color=saved,
                command=_make_cmd(var, holder),
            )
            holder[0] = btn
            setattr(self, f"{attr}_btn", btn)
            btn.grid(row=i, column=1, sticky="w", padx=(0, 12), pady=3)

        ctk.CTkButton(
            cfg, text="Save Settings", height=32, corner_radius=8,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._save_settings,
        ).grid(row=10, column=0, columnspan=2, sticky="e", padx=12, pady=(6, 10))

    def _copy_url(self):
        url = f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/music-player"
        self.app.clipboard_clear()
        self.app.clipboard_append(url)
        self._copy_btn.configure(text="Copied!")
        self.after(1500, lambda: self._copy_btn.configure(text="Copy URL"))

    def _save_settings(self):
        try:
            max_q = max(1, int(self._max_queue_var.get() or 10))
            min_c = max(0, int(self._min_coins_var.get() or 0))
        except ValueError:
            return
        state.config["music_max_queue"] = max_q
        state.config["music_min_coins"] = min_c
        state.config["music_color_song"]        = self._song_color_var.get()
        state.config["music_color_artist"]      = self._artist_color_var.get()
        state.config["music_color_user"]        = self._user_color_var.get()
        state.config["music_color_queue_label"] = self._qlabel_color_var.get()
        state.config["music_color_queue_index"] = self._qindex_color_var.get()
        state.config["music_color_queue_song"]  = self._qsong_color_var.get()
        state.config["music_color_queue_by"]    = self._qby_color_var.get()
        save_config()
        import app.features.comment_player as cp
        cp._MAX_QUEUE = max_q
        cp._broadcast()
        self.app.log(f"[Music] Settings saved — queue max {max_q}, min coins {min_c}", "info")
