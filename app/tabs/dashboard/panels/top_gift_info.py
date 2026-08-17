import customtkinter as ctk

import app.state as state
from app.constants import C_CARD2, C_TEXT, C_MUTED, C_BORDER, C_YELLOW
from app.widgets import make_card, make_label


class TopGiftInfoPanel(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._build()

    def _build(self):
        card = make_card(self)
        card.pack(fill="both", expand=True)

        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(fill="x", padx=12, pady=(10, 6))
        make_label(hdr, "👑  Top Gift", 12, bold=True, color="#ffd45c").pack(side="left")
        self._clear_btn = ctk.CTkButton(
            hdr, text="Clear", width=54, height=22,
            fg_color="#1e1e40", hover_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 10),
            command=self._clear,
        )

        self._body = ctk.CTkFrame(card, fg_color="transparent")
        self._body.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self._empty_lbl = make_label(self._body, "No record this session", 12, color=C_MUTED)
        self._record_row = None
        self.update_record()

    def _clear(self):
        state.top_gift.clear()
        from app.features.top_gift import broadcast_record
        broadcast_record()
        self.update_record()

    def update_record(self):
        if self._record_row:
            self._record_row.destroy()
            self._record_row = None

        username = state.top_gift.get("username", "")
        coins    = state.top_gift.get("coins", 0)

        if not username or not coins:
            if not self._empty_lbl.winfo_ismapped():
                self._empty_lbl.pack(pady=40)
            self._clear_btn.pack_forget()
            return

        self._empty_lbl.pack_forget()
        if not self._clear_btn.winfo_ismapped():
            self._clear_btn.pack(side="right")

        row = ctk.CTkFrame(self._body, fg_color=C_CARD2, corner_radius=8)
        row.pack(fill="x", pady=3)
        make_label(row, "👑", 28).pack(side="left", padx=(12, 10), pady=10)
        make_label(row, username, 13, bold=True, color=C_TEXT).pack(
            side="left", fill="x", expand=True, pady=10
        )
        make_label(row, f"{coins:,} 💎", 13, bold=True, color="#ffd45c").pack(
            side="right", padx=(8, 14), pady=10
        )
        self._record_row = row
