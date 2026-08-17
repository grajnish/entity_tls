import customtkinter as ctk

import app.state as state
from app.config import save_config
from app.constants import C_ACCENT, C_ACCENTL, C_CARD2, C_MUTED, C_TEXT, OVERLAY_HTTP_PORT
from app.widgets import make_help


class GiftRainSection(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        ctk.CTkLabel(
            self,
            text="Gift images rain down from the top of the screen whenever a gift is sent.",
            font=ctk.CTkFont("Segoe UI", 11),
            text_color=C_MUTED,
            justify="left",
        ).pack(anchor="w", padx=12, pady=(8, 10))

        # -- Overlay URL
        url_row = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        url_row.pack(fill="x", padx=10, pady=(0, 10))
        ctk.CTkLabel(
            url_row,
            text=f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/gift-rain",
            font=ctk.CTkFont("Consolas", 10),
            text_color=C_TEXT,
        ).pack(side="left", padx=(12, 4), pady=8)
        make_help(
            url_row,
            "Add this URL as a Link Source in TikTok LIVE Studio\nto display the gift rain overlay.",
        ).pack(side="left", padx=(0, 4), pady=8)
        self._copy_btn = ctk.CTkButton(
            url_row, text="Copy URL", width=90, height=26,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._copy_url,
        )
        self._copy_btn.pack(side="right", padx=8, pady=6)

        # -- Settings
        cfg = ctk.CTkFrame(self, fg_color=C_CARD2, corner_radius=8)
        cfg.pack(fill="x", padx=10, pady=(0, 12))
        cfg.columnconfigure(1, weight=1)

        ctk.CTkLabel(cfg, text="Overlay Settings",
            font=ctk.CTkFont("Segoe UI", 11, "bold"), text_color=C_TEXT,
        ).grid(row=0, column=0, columnspan=2, sticky="w", padx=12, pady=(10, 6))

        # Enabled
        self._enabled_var = ctk.BooleanVar(value=state.config.get("gift_rain_enabled", True))
        ctk.CTkLabel(cfg, text="Enabled", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=1, column=0, sticky="w", padx=(12, 8), pady=4)
        ctk.CTkSwitch(cfg, variable=self._enabled_var, text="",
            onvalue=True, offvalue=False, command=self._save,
        ).grid(row=1, column=1, sticky="w", pady=4)

        # Fall speed
        self._speed_var = ctk.StringVar(value=state.config.get("gift_rain_speed", "normal"))
        ctk.CTkLabel(cfg, text="Fall Speed", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=2, column=0, sticky="w", padx=(12, 8), pady=4)
        ctk.CTkSegmentedButton(cfg, values=["slow", "normal", "fast"],
            variable=self._speed_var, command=lambda _: self._save(),
            font=ctk.CTkFont("Segoe UI", 10),
        ).grid(row=2, column=1, sticky="w", pady=4)

        # Icon size
        self._size_var = ctk.IntVar(value=state.config.get("gift_rain_size", 56))
        ctk.CTkLabel(cfg, text="Icon Size (px)", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=3, column=0, sticky="w", padx=(12, 8), pady=4)
        size_row = ctk.CTkFrame(cfg, fg_color="transparent")
        size_row.grid(row=3, column=1, sticky="w", pady=4)
        self._size_label = ctk.CTkLabel(size_row, text=str(self._size_var.get()),
            width=34, font=ctk.CTkFont("Segoe UI", 11), text_color=C_TEXT,
        )
        self._size_label.pack(side="left")
        ctk.CTkSlider(size_row, from_=24, to=120, number_of_steps=96,
            variable=self._size_var, width=160,
            command=self._on_size_slide,
        ).pack(side="left", padx=(4, 0))

        # Max simultaneous drops
        self._max_var = ctk.IntVar(value=state.config.get("gift_rain_max_drops", 30))
        ctk.CTkLabel(cfg, text="Max Drops", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=4, column=0, sticky="w", padx=(12, 8), pady=(4, 12))
        max_row = ctk.CTkFrame(cfg, fg_color="transparent")
        max_row.grid(row=4, column=1, sticky="w", pady=(4, 12))
        self._max_label = ctk.CTkLabel(max_row, text=str(self._max_var.get()),
            width=34, font=ctk.CTkFont("Segoe UI", 11), text_color=C_TEXT,
        )
        self._max_label.pack(side="left")
        ctk.CTkSlider(max_row, from_=1, to=80, number_of_steps=79,
            variable=self._max_var, width=160,
            command=self._on_max_slide,
        ).pack(side="left", padx=(4, 0))

        # Pile up
        self._pile_var = ctk.BooleanVar(value=state.config.get("gift_rain_pile", True))
        ctk.CTkLabel(cfg, text="Pile Up", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=5, column=0, sticky="w", padx=(12, 8), pady=4)
        ctk.CTkSwitch(cfg, variable=self._pile_var, text="",
            onvalue=True, offvalue=False, command=self._save,
        ).grid(row=5, column=1, sticky="w", pady=4)

        # Drift
        self._drift_var = ctk.BooleanVar(value=state.config.get("gift_rain_drift", True))
        ctk.CTkLabel(cfg, text="Drift (swing)", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=6, column=0, sticky="w", padx=(12, 8), pady=4)
        ctk.CTkSwitch(cfg, variable=self._drift_var, text="",
            onvalue=True, offvalue=False, command=self._save,
        ).grid(row=6, column=1, sticky="w", pady=4)

        # Spawn zone
        self._zone_var = ctk.StringVar(value=state.config.get("gift_rain_spawn_zone", "full"))
        ctk.CTkLabel(cfg, text="Spawn Zone", width=120, anchor="w",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED,
        ).grid(row=7, column=0, sticky="w", padx=(12, 8), pady=(4, 12))
        ctk.CTkSegmentedButton(cfg, values=["full", "center"],
            variable=self._zone_var, command=lambda _: self._save(),
            font=ctk.CTkFont("Segoe UI", 10),
        ).grid(row=7, column=1, sticky="w", pady=(4, 12))

    def _on_size_slide(self, val):
        self._size_label.configure(text=str(int(val)))
        self._save()

    def _on_max_slide(self, val):
        self._max_label.configure(text=str(int(val)))
        self._save()

    def _save(self):
        state.config["gift_rain_enabled"]   = self._enabled_var.get()
        state.config["gift_rain_speed"]     = self._speed_var.get()
        state.config["gift_rain_size"]      = int(self._size_var.get())
        state.config["gift_rain_max_drops"] = int(self._max_var.get())
        state.config["gift_rain_pile"]      = self._pile_var.get()
        state.config["gift_rain_drift"]     = self._drift_var.get()
        state.config["gift_rain_spawn_zone"]= self._zone_var.get()
        save_config()

    def _copy_url(self):
        url = f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/gift-rain"
        self.clipboard_clear()
        self.clipboard_append(url)
        self._copy_btn.configure(text="Copied!")
        self.after(1800, lambda: self._copy_btn.configure(text="Copy URL"))
