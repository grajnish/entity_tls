import random
import customtkinter as ctk

import app.state as state
from app.constants import (
    C_ACCENT, C_ACCENTL, C_CARD2, C_RED, C_MUTED, C_BORDER,
)
from app.widgets import make_card, make_label, make_help

_RANDOM_NAMES = [
    "StarDust99", "NeonRider", "CryptoKing", "FlameWolf", "LunaVibes",
    "ShadowFox", "TurboAce", "BlazePeak", "CosmicJay", "VelvetStorm",
    "ZephyrX", "PixelKnight", "NovaHawk", "EchoBlaze", "TidalWave7",
]

# Approximate TikTok gift catalog (name / coin value / display emoji)
_GIFT_CATALOG = [
    {"name": "Rose",      "coins": 1,     "emoji": "🌹"},
    {"name": "TikTok",    "coins": 1,     "emoji": "🎵"},
    {"name": "Heart",     "coins": 5,     "emoji": "❤️"},
    {"name": "Panda",     "coins": 10,    "emoji": "🐼"},
    {"name": "Love Bang", "coins": 25,    "emoji": "💥"},
    {"name": "Flame",     "coins": 99,    "emoji": "🔥"},
    {"name": "Boxing",    "coins": 100,   "emoji": "🥊"},
    {"name": "Sports Car","coins": 500,   "emoji": "🏎"},
    {"name": "Galaxy",    "coins": 1000,  "emoji": "🌌"},
    {"name": "Lion",      "coins": 2999,  "emoji": "🦁"},
    {"name": "Universe",  "coins": 9999,  "emoji": "🌍"},
    {"name": "Dragon",    "coins": 29999, "emoji": "🐉"},
]


class SimulatePanel(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._catalog_btns: dict = {}
        self._selected_gift: dict = {}
        self._build()

    def _build(self):
        # ── Shared sender row ─────────────────────────────────────────────
        sender_card = make_card(self)
        sender_card.pack(fill="x", pady=(0, 6))
        s_hdr = ctk.CTkFrame(sender_card, fg_color="transparent")
        s_hdr.pack(fill="x", padx=14, pady=(10, 4))
        make_label(s_hdr, "SENDER", 9, color=C_MUTED).pack(side="left")
        make_help(
            s_hdr,
            "Username used for both gift and like simulations.\n"
            "Tick rand to pick a random name on each fire.",
        ).pack(side="right")
        s_row = ctk.CTkFrame(sender_card, fg_color="transparent")
        s_row.pack(fill="x", padx=14, pady=(0, 10))
        self._sim_name_var = ctk.StringVar(value="TestUser")
        self._name_entry = ctk.CTkEntry(
            s_row, textvariable=self._sim_name_var,
            height=32, corner_radius=8,
            fg_color=C_CARD2, border_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 12),
            placeholder_text="@username",
        )
        self._name_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._rand_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            s_row, text="rand", variable=self._rand_var,
            width=50, height=32, checkbox_width=16, checkbox_height=16,
            corner_radius=4, fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 10), text_color=C_MUTED,
            command=self._toggle_rand,
        ).pack(side="left")

        # ── Gift simulation card ──────────────────────────────────────────
        gift_card = make_card(self)
        gift_card.pack(fill="x", pady=(0, 6))
        g_hdr = ctk.CTkFrame(gift_card, fg_color="transparent")
        g_hdr.pack(fill="x", padx=14, pady=(10, 6))
        make_label(g_hdr, "⚡  SIMULATE GIFT", 11, bold=True, color=C_ACCENTL).pack(side="left")
        make_help(
            g_hdr,
            "Fire a fake gift — triggers JJ Video + Gift Leaderboard handlers.\n"
            "Applies streak accumulation for coins < 10.",
        ).pack(side="right")

        catalog_wrap = ctk.CTkFrame(gift_card, fg_color="transparent")
        catalog_wrap.pack(fill="x", padx=12, pady=(0, 4))
        row1 = ctk.CTkFrame(catalog_wrap, fg_color="transparent")
        row1.pack(fill="x", pady=(0, 4))
        row2 = ctk.CTkFrame(catalog_wrap, fg_color="transparent")
        row2.pack(fill="x")
        for i, gift in enumerate(_GIFT_CATALOG):
            parent_row = row1 if i < 6 else row2
            btn = ctk.CTkButton(
                parent_row,
                text=f"{gift['emoji']}\n{gift['name']}\n{gift['coins']}c",
                width=62, height=72, corner_radius=10, border_width=1,
                font=ctk.CTkFont("Segoe UI", 9),
                text_color="white",
                command=lambda g=gift: self._select_gift(g),
            )
            btn.pack(side="left", padx=(0, 4))
            self._catalog_btns[gift["name"]] = btn
        self._select_gift(_GIFT_CATALOG[3])  # default: Panda 10c

        g_bottom = ctk.CTkFrame(gift_card, fg_color="transparent")
        g_bottom.pack(fill="x", padx=14, pady=(6, 10))
        self._custom_var = ctk.StringVar(value="")
        ctk.CTkEntry(
            g_bottom, textvariable=self._custom_var,
            width=100, height=28, corner_radius=8,
            fg_color=C_CARD2, border_color=C_BORDER,
            font=ctk.CTkFont("Consolas", 10),
            placeholder_text="Custom coins…",
        ).pack(side="left", padx=(0, 8))
        make_label(g_bottom, "Count", 11, color=C_MUTED).pack(side="left", padx=(0, 4))
        self._sim_count_var = ctk.StringVar(value="1")
        ctk.CTkEntry(
            g_bottom, textvariable=self._sim_count_var,
            width=52, height=28, corner_radius=8,
            fg_color=C_CARD2, border_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 11), justify="center",
        ).pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            g_bottom, text="🎁  FIRE GIFT", height=28, corner_radius=8,
            fg_color=C_RED, hover_color="#c0392b",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._simulate_gift,
        ).pack(side="right")

        # ── Like simulation card ──────────────────────────────────────────
        like_card = make_card(self)
        like_card.pack(fill="x", pady=(0, 6))
        l_hdr = ctk.CTkFrame(like_card, fg_color="transparent")
        l_hdr.pack(fill="x", padx=14, pady=(10, 6))
        make_label(l_hdr, "❤️  SIMULATE LIKE", 11, bold=True, color="#ff6080").pack(side="left")
        make_help(l_hdr, "Fire fake likes — triggers Top Like handler.").pack(side="right")
        l_row = ctk.CTkFrame(like_card, fg_color="transparent")
        l_row.pack(fill="x", padx=14, pady=(0, 10))
        make_label(l_row, "Count", 11, color=C_MUTED).pack(side="left", padx=(0, 6))
        self._like_count_var = ctk.StringVar(value="10")
        ctk.CTkEntry(
            l_row, textvariable=self._like_count_var,
            width=60, height=28, corner_radius=8,
            fg_color=C_CARD2, border_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 11), justify="center",
        ).pack(side="left", padx=(0, 12))
        ctk.CTkButton(
            l_row, text="❤️  FIRE LIKE", height=28, corner_radius=8,
            fg_color="#b03060", hover_color="#8b1a2e",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._simulate_like,
        ).pack(side="right")

        # ── Comment / !play simulation card ──────────────────────────────
        comment_card = make_card(self)
        comment_card.pack(fill="x", pady=(0, 6))
        c_hdr = ctk.CTkFrame(comment_card, fg_color="transparent")
        c_hdr.pack(fill="x", padx=14, pady=(10, 6))
        make_label(c_hdr, "🎵  SIMULATE COMMENT", 11, bold=True, color="#a0d0ff").pack(side="left")
        make_help(c_hdr, "Fires a fake chat comment — triggers the !play music handler.").pack(side="right")
        c_row = ctk.CTkFrame(comment_card, fg_color="transparent")
        c_row.pack(fill="x", padx=14, pady=(0, 10))
        self._comment_var = ctk.StringVar(value="!play ")
        ctk.CTkEntry(
            c_row, textvariable=self._comment_var,
            height=28, corner_radius=8,
            fg_color=C_CARD2, border_color=C_BORDER,
            font=ctk.CTkFont("Consolas", 11),
            placeholder_text="!play song title - artist",
        ).pack(side="left", fill="x", expand=True, padx=(0, 8))
        ctk.CTkButton(
            c_row, text="💬  FIRE", height=28, corner_radius=8,
            fg_color="#1a5080", hover_color="#2176ae",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self._simulate_comment,
        ).pack(side="right")
        self._is_mod_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            c_row, text="Mod", variable=self._is_mod_var,
            width=60, height=28, checkbox_width=16, checkbox_height=16,
            font=ctk.CTkFont("Segoe UI", 11),
        ).pack(side="right", padx=(0, 6))

    def _toggle_rand(self):
        self._name_entry.configure(
            state="disabled" if self._rand_var.get() else "normal"
        )

    def _get_username(self):
        if self._rand_var.get():
            name = random.choice(_RANDOM_NAMES)
            self._sim_name_var.set(name)
            return name
        return self._sim_name_var.get().strip() or "TestUser"

    def _select_gift(self, gift: dict):
        self._selected_gift = gift
        for name, btn in self._catalog_btns.items():
            if name == gift["name"]:
                btn.configure(fg_color=C_ACCENT, hover_color=C_ACCENTL, border_color="#ffffff")
            else:
                btn.configure(fg_color="#1a1a30", hover_color=C_ACCENT, border_color=C_MUTED)

    def _simulate_gift(self):
        custom = self._custom_var.get().strip()
        try:
            coins = int(custom) if custom else self._selected_gift.get("coins", 10)
            count = max(1, int(self._sim_count_var.get() or 1))
        except ValueError:
            return
        username = self._get_username()
        gift_name = self._selected_gift.get("name", "") if not custom else ""
        label = f"{self._selected_gift.get('emoji', '')} {gift_name}  ({coins}c)" if gift_name else f"{coins}c"
        if coins < 10:
            total = coins * count
            if total < 10:
                self.app.log(
                    f"Streak too small  ({coins}c × {count})  — total {total}c below minimum tier",
                    "warn",
                )
                effective, play_count = 0, 0
            else:
                effective, play_count = total, 1
        else:
            effective, play_count = coins, count
        self.app.log(f"🎁  Simulated  {count}× {label}  from  {username}", "info")
        sim_icon = self._selected_gift.get("emoji", "") if not custom else ""
        for handler in state.raw_gift_handlers:
            handler(coins, count, sim_icon)
        for handler in state.gift_handlers:
            handler(effective, play_count, self.app, username, coins * count, coins, sim_icon)

    def _simulate_like(self):
        try:
            like_count = max(1, int(self._like_count_var.get() or 1))
        except ValueError:
            return
        username = self._get_username()
        self.app.log(f"❤️  Simulated  {like_count} likes  from  {username}", "info")
        for handler in state.like_handlers:
            handler(like_count, self.app, username)

    def _simulate_comment(self):
        text = self._comment_var.get().strip()
        if not text:
            return
        username = self._get_username()
        is_mod = self._is_mod_var.get()
        self.app.log(f"💬  Simulated comment from {username}: {text}", "info")
        for handler in state.comment_handlers:
            handler(text, username, self.app, is_mod)

