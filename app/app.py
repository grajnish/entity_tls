import asyncio
import datetime
import os
from threading import Thread

import customtkinter as ctk

import app.state as state
from app.constants import (
    APP_NAME, VERSION,
    C_BG, C_CARD, C_CARD2, C_SIDEBAR, C_ACCENT, C_ACCENTL,
    C_GREEN, C_MUTED, C_BORDER, C_TEXT,
    OVERLAY_HTTP_PORT, OVERLAY_WS_PORT,
)
from app.features.jj_video import video_worker
from app.server import start_overlay_server, stop_overlay_server
from app.tiktok import _run_tiktok
from app.widgets import make_card, make_label, set_icon
from app.tabs.dashboard.dashboard import DashboardPage
from app.tabs.features.features import FeaturesPage
from app.tabs.settings.settings import SettingsPage
from app.tabs.log.log import LogPage
from app.tabs.tutorial.tutorial import TutorialPage


class _ServerInfoModal(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.overrideredirect(True)
        self.geometry("540x480")
        self.configure(fg_color=C_BG)
        self.grab_set()
        set_icon(self)
        self._build()
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        px = (sw - self.winfo_width())  // 2
        py = (sh - self.winfo_height()) // 2
        self.geometry(f"+{px}+{py}")

    def _build(self):
        make_label(self, "✔  SERVER CONNECTED", 17, bold=True, color=C_GREEN).pack(pady=(22, 4))
        make_label(self, "Add each URL as a separate LINK Source in TikTok Live Studio.",
                   10, color=C_MUTED).pack(pady=(0, 14))

        card = make_card(self)
        card.pack(fill="x", padx=22, pady=(0, 14))

        pr = ctk.CTkFrame(card, fg_color="transparent")
        pr.pack(fill="x", padx=14, pady=(12, 8))
        make_label(pr, f"HTTP :{OVERLAY_HTTP_PORT}", 11, bold=True, color=C_TEXT).pack(side="left", padx=(0, 18))
        make_label(pr, f"WS :{OVERLAY_WS_PORT}", 11, color=C_MUTED).pack(side="left")

        self._copy_btns = {}
        overlays = [
            ("🎬  JJ Video",         f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/jj-video"),
            ("🏆  Gift Leaderboard", f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/gift-leaderboard"),
            ("❤️  Top Like",        f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/top-like"),
            ("👑  Top Gift",         f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/top-gift"),
            ("🎵  Music Player",     f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/music-player"),
            ("🌧️  Gift Rain",        f"http://entity.tls:{OVERLAY_HTTP_PORT}/overlay/gift-rain"),
        ]
        scroll = ctk.CTkScrollableFrame(card, fg_color="transparent", height=260)
        scroll.pack(fill="x", padx=6, pady=(0, 6))
        for label, url in overlays:
            make_label(scroll, label, 9, color=C_MUTED).pack(anchor="w", padx=8, pady=(0, 2))
            url_row = ctk.CTkFrame(scroll, fg_color=C_CARD2, corner_radius=8)
            url_row.pack(fill="x", padx=8, pady=(0, 8))
            make_label(url_row, url, 9, color=C_TEXT).pack(side="left", padx=(10, 0), pady=8)
            btn = ctk.CTkButton(
                url_row, text="⎘  Copy", width=70, height=26,
                fg_color=C_ACCENT, hover_color=C_ACCENTL,
                font=ctk.CTkFont("Segoe UI", 10),
                command=lambda u=url, lbl=label: self._copy(u, lbl),
            )
            btn.pack(side="right", padx=8, pady=6)
            self._copy_btns[label] = btn

        ctk.CTkButton(
            self, text="Got it", height=44, corner_radius=10,
            fg_color=C_CARD, hover_color=C_BORDER,
            font=ctk.CTkFont("Segoe UI", 12),
            command=self.destroy,
        ).pack(fill="x", padx=22, pady=(0, 18))

    def _copy(self, url, label):
        self.clipboard_clear()
        self.clipboard_append(url)
        btn = self._copy_btns[label]
        btn.configure(text="✓  Copied!", fg_color=C_GREEN)
        self.after(1500, lambda: btn.configure(text="⎘  Copy", fg_color=C_ACCENT))


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()  # hidden until splash finishes

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.configure(fg_color=C_BG)

        from app.loader import SplashScreen
        splash = SplashScreen(self)
        splash.on_done = self._after_splash

    def _after_splash(self):
        self.title(f"{APP_NAME}  —  v{VERSION}")
        w, h = 960, 700
        self.geometry(f"{w}x{h}")
        self.minsize(800, 600)
        self.update_idletasks()
        sx = (self.winfo_screenwidth()  - w) // 2
        sy = (self.winfo_screenheight() - h) // 2
        self.geometry(f"{w}x{h}+{sx}+{sy}")

        self._monitoring = False
        self._build()
        self._nav("dashboard")
        state._app_ref = self
        set_icon(self)

        Thread(target=video_worker, args=(self,), daemon=True).start()
        self.deiconify()

    # ── Layout ────────────────────────────────────────────────
    def _build(self):
        self._build_sidebar()

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(side="left", fill="both", expand=True, padx=22, pady=22)

        self.pages = {
            "dashboard": DashboardPage(self.content, self),
            "features":  FeaturesPage(self.content, self),
            "settings":  SettingsPage(self.content, self),
            "tutorial":  TutorialPage(self.content, self),
            "log":       LogPage(self.content, self),
        }

    def _build_sidebar(self):
        sb = ctk.CTkFrame(self, width=210, fg_color=C_SIDEBAR, corner_radius=0)
        sb.pack(side="left", fill="y")
        sb.pack_propagate(False)

        logo = ctk.CTkFrame(sb, fg_color="#09091e", height=76, corner_radius=0)
        logo.pack(fill="x")
        logo.pack_propagate(False)

        inner = ctk.CTkFrame(logo, fg_color="transparent")
        inner.place(relx=0.5, rely=0.5, anchor="center")
        ctk.CTkLabel(inner, text="ENTITY",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=C_ACCENT).pack(side="left")
        ctk.CTkLabel(inner, text=" TLS",
                     font=ctk.CTkFont("Segoe UI", 20, "bold"),
                     text_color=C_TEXT).pack(side="left")

        ctk.CTkFrame(sb, fg_color=C_BORDER, height=1).pack(fill="x", pady=(0, 10))

        self._nav_btns = {}
        for key, icon, label in [
            ("dashboard", "🏠", "Dashboard"),
            ("features",  "✨", "Features"),
            ("settings",  "⚙", "Settings"),
            ("tutorial",  "📖", "Tutorial"),
            ("log",       "📋", "Log"),
        ]:
            btn = ctk.CTkButton(
                sb, text=f"  {icon}  {label}", anchor="w",
                height=46, corner_radius=10,
                font=ctk.CTkFont("Segoe UI", 13),
                fg_color="transparent", hover_color="#161630",
                text_color=C_MUTED, border_width=0,
                command=lambda k=key: self._nav(k),
            )
            btn.pack(fill="x", padx=10, pady=2)
            self._nav_btns[key] = btn

        ctk.CTkFrame(sb, fg_color=C_BORDER, height=1).pack(fill="x", side="bottom", pady=(0, 50))
        make_label(sb, f"v{VERSION}", 10, color=C_MUTED).pack(side="bottom", pady=4)
        make_label(sb, APP_NAME, 10, bold=True, color=C_MUTED).pack(side="bottom", pady=2)

    def _nav(self, key):
        for k, page in self.pages.items():
            page.pack_forget() if k != key else page.pack(fill="both", expand=True)

        for k, btn in self._nav_btns.items():
            btn.configure(
                fg_color="#18183a" if k == key else "transparent",
                text_color=C_ACCENTL if k == key else C_MUTED,
            )

    # ── Overlay server ────────────────────────────────────────
    def toggle_overlay_server(self):
        if state._overlay_connected:
            Thread(target=stop_overlay_server, args=(self,), daemon=True).start()
        else:
            Thread(target=start_overlay_server, args=(self,), daemon=True).start()

    # ── Monitoring ────────────────────────────────────────────
    def toggle_monitoring(self):
        if self._monitoring:
            self._stop_monitoring()
        else:
            self._start_monitoring()

    def _start_monitoring(self):
        state.session_start = datetime.datetime.now()
        state.videos_played = 0
        state._recent_playbacks.clear()
        state.gift_leaderboard.clear()
        state.top_likes.clear()
        state.top_gift.clear()
        d = self.pages["dashboard"]
        d.set_played(0)
        d.update_playbacks()
        d.update_gift_leaderboard()
        d.update_top_likes()
        d.update_top_gift()
        self.set_monitoring(True)
        self._tick_timer()
        Thread(target=_run_tiktok, args=(self,), daemon=True).start()

    def _stop_monitoring(self):
        self.log("Stopping TikTok LIVE monitoring...", "warn")
        try:
            if state.tiktok_client and state.tiktok_loop and state.tiktok_loop.is_running():
                asyncio.run_coroutine_threadsafe(state.tiktok_client.disconnect(), state.tiktok_loop)
        except Exception as e:
            self.log(f"Stop error: {e}", "error")
        self.set_monitoring(False)

    # ── Thread-safe updates ───────────────────────────────────
    def set_monitoring(self, active):
        self._monitoring = active
        self.after(0, lambda: self.pages["dashboard"].set_monitoring_btn(active))

    def set_overlay_status(self, active):
        self.after(0, lambda: self.pages["dashboard"].set_overlay_status(active))

    def set_tiktok_status(self, connected):
        self.after(0, lambda: self.pages["dashboard"].set_tiktok_status(connected))

    def refresh_stats(self):
        self.after(0, lambda: self.pages["dashboard"].set_queue(state.video_queue.qsize()))

    def set_clients_count(self, count):
        self.after(0, lambda: self.pages["dashboard"].set_clients_count(count))

    def refresh_gift_leaderboard(self):
        self.after(0, lambda: self.pages["dashboard"].update_gift_leaderboard())

    def refresh_top_likes(self):
        self.after(0, lambda: self.pages["dashboard"].update_top_likes())

    def refresh_top_gift(self):
        self.after(0, lambda: self.pages["dashboard"].update_top_gift())

    def increment_videos_played(self):
        def _upd():
            d = self.pages["dashboard"]
            d.set_played(state.videos_played)
            d.update_playbacks()
        self.after(0, _upd)

    def _tick_timer(self):
        if not self._monitoring or state.session_start is None:
            self.pages["dashboard"].set_timer("00:00:00")
            return
        elapsed = int((datetime.datetime.now() - state.session_start).total_seconds())
        h, rem = divmod(elapsed, 3600)
        m, s   = divmod(rem, 60)
        self.pages["dashboard"].set_timer(f"{h:02d}:{m:02d}:{s:02d}")
        self.after(1000, self._tick_timer)

    def set_playing(self, name):
        self.after(0, lambda: self.pages["dashboard"].set_playing(name))

    def show_server_modal(self):
        self.after(0, lambda: _ServerInfoModal(self))

    def log(self, message, tag="info"):
        def _upd():
            self.pages["log"].write(message, tag)
        self.after(0, _upd)
