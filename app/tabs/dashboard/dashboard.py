import customtkinter as ctk

import app.state as state
from app.constants import (
    OVERLAY_HTTP_PORT, OVERLAY_WS_PORT,
    C_CARD, C_CARD2, C_ACCENT, C_ACCENTL,
    C_GREEN, C_RED, C_YELLOW, C_TEXT, C_MUTED, C_BORDER,
)
from app.tabs.dashboard.panels.jj_video_info import JJVideoInfoPanel
from app.tabs.dashboard.panels.gift_leaderboard_info import GiftLeaderboardInfoPanel
from app.tabs.dashboard.panels.top_like_info import TopLikeInfoPanel
from app.tabs.dashboard.panels.top_gift_info import TopGiftInfoPanel
from app.tabs.dashboard.panels.simulation_panel import SimulatePanel
from app.tabs.dashboard.panels.music_player_panel import MusicPlayerPanel
from app.widgets import make_card, make_label, make_help



class DashboardPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        self._build_status_row()
        self._build_main_content()

    def _build_status_row(self):
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack(fill="x", pady=(0, 8))
        row.columnconfigure((0, 1, 2), weight=1)

        # ── Overlay card
        ov_card = make_card(row)
        ov_card.grid(row=0, column=0, sticky="nsew", padx=(0, 6))
        ov_hdr = ctk.CTkFrame(ov_card, fg_color="transparent")
        ov_hdr.pack(fill="x", padx=14, pady=(10, 2))
        make_label(ov_hdr, "OVERLAY SERVER", 9, color=C_MUTED).pack(side="left")
        make_help(ov_hdr, "Local HTTP server that serves the transparent video overlay page.").pack(side="right")
        ctk.CTkFrame(ov_card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))
        self.overlay_status = make_label(ov_card, "⬤  OFFLINE", 13, bold=True, color=C_RED)
        self.overlay_status.pack(anchor="w", padx=14, pady=(0, 2))
        make_label(ov_card, f"ENTITY WILL RUN ON LOCALHOST", 10, color=C_MUTED).pack(anchor="w", padx=14, pady=(0, 6))
        self.overlay_btn = ctk.CTkButton(
            ov_card, text="▶  CONNECT", height=28, corner_radius=8,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self.app.toggle_overlay_server,
        )
        self.overlay_btn.pack(anchor="w", padx=14, pady=(0, 10))

        # ── TikTok card
        tt_card = make_card(row)
        tt_card.grid(row=0, column=1, sticky="nsew", padx=6)
        tt_top = ctk.CTkFrame(tt_card, fg_color="transparent")
        tt_top.pack(fill="x", padx=14, pady=(10, 2))
        make_label(tt_top, "TIKTOK LIVE", 9, color=C_MUTED).pack(side="left")
        make_help(tt_top, "Connects to your TikTok LIVE stream and listens for gift events.\n\nEach gift triggers a video in the overlay queue. The timer shows how long the current session has been running.").pack(side="right")
        self.timer_lbl = make_label(tt_top, "00:00:00", 9, color=C_MUTED)
        self.timer_lbl.pack(side="right", padx=(0, 4))
        ctk.CTkFrame(tt_card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))
        self.tt_status = make_label(tt_card, "⬤  OFFLINE", 13, bold=True, color=C_RED)
        self.tt_status.pack(anchor="w", padx=14, pady=(0, 2))
        self.tt_user = make_label(tt_card, state.config.get("username", "—").upper(), 11, color=C_MUTED)
        self.tt_user.pack(anchor="w", padx=14, pady=(0, 6))
        self.start_btn = ctk.CTkButton(
            tt_card, text="▶  CONNECT", height=28, corner_radius=8,
            fg_color=C_GREEN, hover_color="#00cec9",
            font=ctk.CTkFont("Segoe UI", 11, "bold"),
            command=self.app.toggle_monitoring,
        )
        self.start_btn.pack(anchor="w", padx=14, pady=(0, 10))

        # ── Server info card
        sv_card = make_card(row)
        sv_card.grid(row=0, column=2, sticky="nsew", padx=(6, 0))
        sv_hdr = ctk.CTkFrame(sv_card, fg_color="transparent")
        sv_hdr.pack(fill="x", padx=14, pady=(10, 2))
        make_label(sv_hdr, "SERVER", 9, color=C_MUTED).pack(side="left")
        make_help(sv_hdr, "HTTP port serves the overlay page and video files.\nWS port is the WebSocket that pushes play commands to the browser.\n\nLINKS = number of TikTok LIVE Studio Link Source tabs currently connected.").pack(side="right")
        ctk.CTkFrame(sv_card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))
        pr = ctk.CTkFrame(sv_card, fg_color="transparent")
        pr.pack(fill="x", padx=14, pady=(0, 6))
        make_label(pr, f"HTTP  :{OVERLAY_HTTP_PORT}", 11, bold=True, color=C_TEXT).pack(side="left", padx=(0, 12))
        make_label(pr, f"WS  :{OVERLAY_WS_PORT}", 11, color=C_MUTED).pack(side="left")
        make_label(sv_card, "LINKS", 9, color=C_MUTED).pack(anchor="w", padx=14, pady=(0, 2))
        self.clients_lbl = make_label(sv_card, "0  connected", 11, bold=True, color=C_MUTED)
        self.clients_lbl.pack(anchor="w", padx=14, pady=(0, 10))

    def _build_main_content(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True)

        # breadcrumb tab bar spans full width above the content split
        self._tab_bar = ctk.CTkSegmentedButton(
            main, command=self._switch_tab,
            fg_color=C_CARD, selected_color=C_ACCENT,
            selected_hover_color=C_ACCENTL, unselected_color=C_CARD2,
            unselected_hover_color=C_BORDER, text_color=C_TEXT,
            font=ctk.CTkFont("Segoe UI", 11), corner_radius=6, height=30,
        )
        self._tab_bar.pack(fill="x", pady=(0, 6))

        content = ctk.CTkFrame(main, fg_color="transparent")
        content.pack(fill="both", expand=True)

        left = ctk.CTkFrame(content, fg_color="transparent")
        left.pack(fill="both", expand=True)

        self._panels = {}
        self._jj_panel = JJVideoInfoPanel(left, self.app)
        self._register_panel("🎥  JJ Video", self._jj_panel)
        # forward widget refs so app.py accesses stats without knowing panel internals
        self.queue_lbl   = self._jj_panel.queue_lbl
        self.played_lbl  = self._jj_panel.played_lbl
        self.playing_lbl = self._jj_panel.playing_lbl
        self.status_lbl  = self._jj_panel.status_lbl

        self._top_panel = GiftLeaderboardInfoPanel(left)
        self._register_panel("🏆  Gift Leaderboard", self._top_panel)

        self._like_panel = TopLikeInfoPanel(left)
        self._register_panel("❤️  Top Like", self._like_panel)

        self._gift_panel = TopGiftInfoPanel(left)
        self._register_panel("👑  Top Gift", self._gift_panel)

        self._music_panel = MusicPlayerPanel(left, self.app)
        self._register_panel("🎵  Music Player", self._music_panel)

        self._sim_panel = SimulatePanel(left, self.app)
        self._register_panel("⚡  Simulation", self._sim_panel)

    def _register_panel(self, name, panel):
        """Add a feature panel and show it if it's the first."""
        self._panels[name] = panel
        self._tab_bar.configure(values=list(self._panels.keys()))
        if len(self._panels) == 1:
            self._switch_tab(name)

    def _switch_tab(self, name):
        for panel in self._panels.values():
            panel.pack_forget()
        self._panels[name].pack(fill="both", expand=True)
        self._tab_bar.set(name)


    def update_playbacks(self):
        self._jj_panel.update_playbacks()

    def update_gift_leaderboard(self):
        self._top_panel.update_leaderboard()

    def update_top_likes(self):
        self._like_panel.update_leaderboard()

    def update_top_gift(self):
        self._gift_panel.update_record()

    # ── Named update methods ─────────────────────────────────────
    def set_monitoring_btn(self, active):
        if active:
            self.start_btn.configure(text="⏹  DISCONNECT", fg_color=C_RED, hover_color="#c0392b")
        else:
            self.start_btn.configure(text="▶  CONNECT", fg_color=C_GREEN, hover_color="#00cec9")

    def set_overlay_status(self, active):
        self.overlay_status.configure(
            text="⬤  ONLINE" if active else "⬤  OFFLINE",
            text_color=C_GREEN if active else C_RED,
        )
        self.overlay_btn.configure(
            text="⏹  DISCONNECT" if active else "▶  CONNECT",
            fg_color=C_RED if active else C_ACCENT,
            hover_color="#c0392b" if active else C_ACCENTL,
        )

    def set_tiktok_status(self, connected):
        self.tt_status.configure(
            text="⬤  LIVE" if connected else "⬤  OFFLINE",
            text_color=C_GREEN if connected else C_RED,
        )
        # vivid glow-like colors: bright green on live, soft red on offline
        self.tt_user.configure(text_color="#00e676" if connected else C_MUTED)

    def set_clients_count(self, count):
        self.clients_lbl.configure(
            text=f"{count}  connected",
            text_color=C_GREEN if count > 0 else C_MUTED,
        )

    def set_queue(self, n):
        self.queue_lbl.configure(text=str(n))

    def set_played(self, n):
        self.played_lbl.configure(text=str(n))

    def set_timer(self, text):
        self.timer_lbl.configure(text=text)

    def set_playing(self, name):
        if name:
            short = (name[:16] + "…") if len(name) > 16 else name
            self.playing_lbl.configure(text=short, text_color=C_ACCENTL)
            self.status_lbl.configure(text="PLAYING", text_color=C_ACCENTL)
        else:
            self.playing_lbl.configure(text="IDLE", text_color=C_MUTED)
            q = state.video_queue.qsize()
            self.status_lbl.configure(
                text="QUEUED" if q > 0 else "READY",
                text_color=C_YELLOW if q > 0 else C_GREEN,
            )
