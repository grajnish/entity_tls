import customtkinter as ctk

import app.state as state
from app.constants import C_ACCENTL, C_CARD2, C_TEXT, C_MUTED, C_BORDER
from app.widgets import make_card, make_label

_RANK_COLORS = {1: "#f9ca24", 2: "#b2bec3", 3: "#d4a96a"}


class GiftLeaderboardInfoPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._rows = []
        self._build()

    def _build(self):
        card = make_card(self)
        card.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        make_label(hdr, "🏆  Gift Leaderboard", 12, bold=True, color=C_ACCENTL).pack(side="left")
        self._clear_btn = ctk.CTkButton(
            hdr, text="Clear", width=54, height=22,
            fg_color="#1e1e40", hover_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._clear,
        )

        self._body = ctk.CTkFrame(card, fg_color="transparent")
        self._body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._empty_lbl = make_label(self._body, "No gifters yet this session", 12, color=C_MUTED)
        self.update_leaderboard()

    def _clear(self):
        state.gift_leaderboard.clear()
        from app.features.gift_leaderboard import broadcast_leaderboard
        broadcast_leaderboard()
        self.update_leaderboard()

    def update_leaderboard(self):
        for w in self._rows:
            w.destroy()
        self._rows = []

        ranked = sorted(state.gift_leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]

        if not ranked:
            if not self._empty_lbl.winfo_ismapped():
                self._empty_lbl.pack(pady=40)
            self._clear_btn.pack_forget()
            return

        self._empty_lbl.pack_forget()
        if not self._clear_btn.winfo_ismapped():
            self._clear_btn.pack(side="right")

        for i, (name, coins) in enumerate(ranked):
            rank = i + 1
            row = ctk.CTkFrame(self._body, fg_color=C_CARD2, corner_radius=8)
            row.pack(fill="x", pady=3)
            rc = _RANK_COLORS.get(rank, C_MUTED)
            make_label(row, f"#{rank}", 13, bold=True, color=rc).pack(side="left", padx=(12, 8), pady=8)
            make_label(row, name, 12, color=C_TEXT).pack(side="left", fill="x", expand=True, pady=8)
            make_label(row, f"{coins:,} 💎", 12, bold=True, color=rc).pack(side="right", padx=(8, 12), pady=8)
            self._rows.append(row)
