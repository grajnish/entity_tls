import customtkinter as ctk

from app.constants import C_BORDER
from app.widgets import make_label, make_logbox, write_log


class LogPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))

        make_label(hdr, "Full Log", 15, bold=True).pack(side="left")

        ctk.CTkButton(
            hdr, text="Clear", width=70, height=30,
            fg_color="#1e1e40", hover_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 11),
            command=self._clear
        ).pack(side="right")

        self.box = make_logbox(self)
        self.box.pack(fill="both", expand=True)

    def _clear(self):
        self.box.configure(state="normal")
        self.box.delete("0.0", "end")
        self.box.configure(state="disabled")

    def write(self, message, tag):
        write_log(self.box, message, tag)
