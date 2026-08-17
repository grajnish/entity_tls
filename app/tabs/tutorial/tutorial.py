import customtkinter as ctk

from app.constants import (
    C_ACCENT, C_ACCENTL, C_BG, C_CARD, C_CARD2,
    C_GREEN, C_MUTED, C_RED, C_TEXT, C_BORDER, C_YELLOW,
    OVERLAY_HTTP_PORT, OVERLAY_WS_PORT,
)
from app.widgets import make_card, make_label


def _heading(parent, text, color=None):
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont("Segoe UI", 13, "bold"),
        text_color=color or C_ACCENTL, anchor="w",
    ).pack(anchor="w", padx=16, pady=(14, 3))


def _divider(parent):
    ctk.CTkFrame(parent, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 8))


def _body(parent, text, color=None):
    ctk.CTkLabel(
        parent, text=text,
        font=ctk.CTkFont("Segoe UI", 11),
        text_color=color or C_MUTED,
        justify="left", anchor="w", wraplength=580,
    ).pack(anchor="w", padx=16, pady=(0, 4))


def _code(parent, text):
    row = ctk.CTkFrame(parent, fg_color=C_CARD2, corner_radius=6)
    row.pack(fill="x", padx=16, pady=(2, 6))
    ctk.CTkLabel(
        row, text=text,
        font=ctk.CTkFont("Consolas", 11),
        text_color=C_ACCENTL, anchor="w", justify="left",
    ).pack(anchor="w", padx=10, pady=6)


def _badge(parent, text, color):
    ctk.CTkLabel(
        parent, text=f"  {text}  ",
        font=ctk.CTkFont("Segoe UI", 10, "bold"),
        text_color="#ffffff", fg_color=color, corner_radius=4,
    ).pack(anchor="w", padx=16, pady=(0, 6))


def _section_card(scroll, title, emoji=""):
    card = make_card(scroll)
    card.pack(fill="x", padx=2, pady=(0, 12))
    label = f"{emoji}  {title}" if emoji else title
    ctk.CTkLabel(
        card, text=label,
        font=ctk.CTkFont("Segoe UI", 14, "bold"),
        text_color=C_TEXT, anchor="w",
    ).pack(anchor="w", padx=16, pady=(14, 2))
    _divider(card)
    return card


class TutorialPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 10))
        make_label(hdr, "Tutorial & Guide", 15, bold=True).pack(side="left")
        make_label(
            hdr, "Complete reference for ENTITY TLS", 11, color=C_MUTED,
        ).pack(side="left", padx=(12, 0), pady=(4, 0))

        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.scroll_frame = scroll
        scroll.pack(fill="both", expand=True)

        self._build_overview(scroll)
        self._build_first_run(scroll)
        self._build_jj_video(scroll)
        self._build_gift_leaderboard(scroll)
        self._build_top_like(scroll)
        self._build_top_gift(scroll)
        self._build_music_player(scroll)
        self._build_simulation(scroll)
        self._build_dashboard(scroll)
        self._build_tips(scroll)

    # ── Sections ──────────────────────────────────────────────────────────────

    def _build_overview(self, scroll):
        card = _section_card(scroll, "What is ENTITY TLS?", "📖")
        _body(card,
            "ENTITY TLS is a TikTok LIVE overlay suite. It listens to your live stream "
            "events (gifts, likes, comments) and reacts in real-time by playing videos "
            "and updating overlay widgets displayed in TikTok LIVE Studio via Link Sources."
        )
        _heading(card, "How it works — in one paragraph")
        _body(card,
            "The app runs two local servers: an HTTP server (port 8765) that serves "
            "overlay HTML pages, and a WebSocket server (port 8766) that pushes live "
            "events to those pages. You add each overlay URL as a Link Source in TIKTOK "
            "LIVE Studio. The app connects to your TikTok LIVE stream and translates "
            "gifts / likes / comments into real-time overlay updates."
        )
        _heading(card, "Overlay URLs")
        for name, path in [
            ("JJ Video",         "overlay/jj-video"),
            ("Gift Leaderboard", "overlay/gift-leaderboard"),
            ("Top Like",         "overlay/top-like"),
            ("Top Gift",         "overlay/top-gift"),
            ("Music Player",     "overlay/music-player"),
        ]:
            _code(card, f"http://entity.tls:{OVERLAY_HTTP_PORT}/{path}    ← {name}")

    def _build_first_run(self, scroll):
        card = _section_card(scroll, "First-Time Setup", "🚀")

        _heading(card, "Step 1 — Hosts file (automatic)")
        _body(card,
            "On first launch the splash screen checks if  entity.tls  is in your Windows "
            "hosts file. If it is missing, it requests administrator access once and adds:"
        )
        _code(card, "127.0.0.1    entity.tls")
        _body(card,
            "This lets your browser resolve  entity.tls  to your own machine so the overlay "
            "URLs work. Approve the UAC prompt if you see one — it only runs once."
        )

        _heading(card, "Step 2 — Settings tab")
        _body(card,
            "Go to  Settings  and enter your TikTok username (with @).  "
            "Set the Music Folder to a folder where yt-dlp will download tracks."
        )

        _heading(card, "Step 3 — Configure tiers (JJ Video)")
        _body(card,
            "In  Features → JJ Video  assign video files to each coin tier "
            "(10, 20, 30, 100 … 2000). "
            "You can assign multiple files per tier — one is picked at random each time. "
            "Set a Default Video that plays when no tier matches."
        )

        _heading(card, "Step 4 — Start the Overlay Server")
        _body(card,
            "On the Dashboard click  ▶ CONNECT  under OVERLAY SERVER. "
            "A modal appears with all overlay URLs — copy each one into a "
            "Link Source widget in TikTok LIVE Studio. Set each source to "
            "transparent background."
        )

        _heading(card, "Step 5 — Connect to TikTok LIVE")
        _body(card,
            "Start your live stream on TikTok first. Then click  ▶ CONNECT  "
            "under TIKTOK LIVE on the Dashboard. The status changes to ONLINE. "
            "The app is now listening for events."
        )

    def _build_jj_video(self, scroll):
        card = _section_card(scroll, "JJ Video — Gift-triggered videos", "🎬")

        _heading(card, "What it does")
        _body(card,
            "When a viewer sends a gift, the app looks up their coin value in the tier "
            "table, picks a random video from that tier, and plays it in the JJ Video "
            "overlay."
        )

        _heading(card, "Coin tiers")
        _body(card,
            "Tiers available: 10, 20, 30, 100, 200, 300, 500, 1000, 2000 coins. "
            "A gift triggers the highest tier whose threshold it meets or exceeds. "
            "For example a 150-coin gift triggers the 100-coin tier."
        )

        _heading(card, "Streaks (small gifts)")
        _body(card,
            "Gifts under 10 coins are accumulated in a streak. Only when the running "
            "total reaches ≥ 10 coins does a single video play at the total value."
        )

        _heading(card, "Default video")
        _body(card,
            "If no tier matches (e.g. a 7-coin gift that never accumulates to 10), "
            "the Default Video plays instead. You can assign multiple default videos."
        )

        _heading(card, "Queue")
        _body(card,
            "Videos queue up — if two gifts arrive while a video is playing, both are "
            "queued and played in order. The Queue counter on the Dashboard shows how "
            "many are waiting."
        )

        _heading(card, "Features tab options")
        _body(card,
            "Each tier row has a  + Add  button to browse for video files. "
            "Multiple files per tier are shown as a list; click × to remove one. "
            "Click  Save Settings  to persist changes."
        )

    def _build_gift_leaderboard(self, scroll):
        card = _section_card(scroll, "Gift Leaderboard", "🏆")
        _heading(card, "What it does")
        _body(card,
            "Tracks total diamonds gifted per viewer for the current live session and "
            "displays the top 5 in the overlay, updated in real-time after every gift."
        )
        _heading(card, "Customization")
        _body(card, "In  Features → Gift Leaderboard  you can change Username Color and Ranking Color. "
                     "Click Save Settings to push the new colors to the overlay immediately.")
        _body(card, "⚠  The leaderboard resets when you disconnect from TikTok LIVE.", C_YELLOW)

    def _build_top_like(self, scroll):
        card = _section_card(scroll, "Top Like", "❤️")
        _heading(card, "What it does")
        _body(card,
            "Shows the top 5 viewers by total like-taps sent during the current session. "
            "Updates after every like batch event from TikTok."
        )
        _heading(card, "Customization")
        _body(card, "Username Color is configurable in  Features → Top Like.")

    def _build_top_gift(self, scroll):
        card = _section_card(scroll, "Top Gift — Single highest gift", "👑")
        _heading(card, "What it does")
        _body(card,
            "Highlights the single most valuable gift received in the session — the "
            "viewer who sent the highest per-event coin value. The overlay shows their "
            "username, the coin amount, the gift icon, and their avatar."
        )
        _heading(card, "Customization")
        _body(card,
            "In  Features → Top Gift  you can change the overlay title text and "
            "three colors: Title, Username, and Holder (coin amount). "
            "Saved changes push to the overlay instantly."
        )

    def _build_music_player(self, scroll):
        card = _section_card(scroll, "Music Player — Chat-requested songs", "🎵")

        _heading(card, "Viewer commands")
        for cmd, desc in [
            ("!play <song title or artist - song>", "Request a song. yt-dlp searches YouTube and queues the audio."),
            ("!cancel",                              "Remove your most recent request from the queue."),
            ("!skip",                                "Moderators (and the streamer) only — skips the current track."),
        ]:
            _code(card, cmd)
            _body(card, f"  {desc}")

        _heading(card, "How it works")
        _body(card,
            "When a viewer sends  !play <query>, the app searches YouTube via yt-dlp, "
            "downloads the audio to a local temp folder, and streams it to the overlay "
            "via your local HTTP server. The overlay plays it in a hidden <audio> element. "
            "Temp files are deleted automatically after each track finishes."
        )

        _heading(card, "Queue rules")
        _body(card,
            "Maximum queue length is set in  Features → Music Player  (default 10). "
            "While a song plays, the next one pre-downloads in the background so "
            "there is no gap between tracks."
        )

        _heading(card, "Min-coins gate")
        _body(card,
            "If  Min Coins  is set to > 0, a viewer must have gifted at least that many "
            "diamonds in the current session before their  !play  requests are accepted."
        )

        _heading(card, "Dashboard controls")
        _body(card,
            "The  Music Player  panel on the Dashboard shows the current track, "
            "requester, queue, and gives you Pause / Resume / Skip / Volume / Clear Queue buttons."
        )

        _heading(card, "Overlay colors")
        _body(card,
            "All text colors (song title, artist, requester, queue items) are "
            "customizable in  Features → Music Player → Save Settings."
        )

    def _build_simulation(self, scroll):
        card = _section_card(scroll, "Simulation — Testing without going live", "⚡")

        _heading(card, "Gift simulation")
        _body(card,
            "Select a gift from the catalog (or type a custom coin value), set the "
            "repeat count, and click  🎁 FIRE GIFT. This fires all registered gift "
            "handlers exactly as if a real gift arrived — videos queue, leaderboard "
            "updates, top-gift updates."
        )

        _heading(card, "Like simulation")
        _body(card, "Set a like count and click  ❤️ FIRE LIKE. Updates the Top Like leaderboard.")

        _heading(card, "Comment simulation (Music Player)")
        _body(card,
            "Type  !play <song>  (or  !skip,  !cancel) in the text box and click "
            "💬 FIRE. Tick  Mod  to simulate a moderator so  !skip  is accepted."
        )

        _heading(card, "Tip")
        _body(card,
            "Enable  rand  on the sender name to auto-pick a random username on each "
            "fire — useful for populating the leaderboard with varied data.", C_MUTED)

    def _build_dashboard(self, scroll):
        card = _section_card(scroll, "Dashboard — At a glance", "🏠")

        _heading(card, "Status cards (top row)")
        for name, desc in [
            ("OVERLAY SERVER", "Start/stop the HTTP+WS servers. Must be ON for overlays to work."),
            ("TIKTOK LIVE",    "Connect to your live stream. Timer shows session duration."),
            ("SERVER",         "Shows HTTP/WS ports and number of connected Link Source tabs."),
        ]:
            _code(card, name)
            _body(card, f"  {desc}")

        _heading(card, "Panel tabs")
        _body(card,
            "Below the status row are tabbed panels: JJ Video stats, leaderboard data, "
            "music player controls, and simulation. Switch between them with the tab bar."
        )

    def _build_tips(self, scroll):
        card = _section_card(scroll, "Tips & Troubleshooting", "💡")

        _heading(card, "Overlay shows blank / no data")
        _body(card,
            "Make sure the Overlay Server is running (green ONLINE) AND the browser "
            "tab in TikTok LIVE Studio is open. The overlay only receives data when "
            "connected via WebSocket."
        )

        _heading(card, "Videos play but immediately finish")
        _body(card,
            "The video file extension must be a supported format (.mp4, .mov, .webm, "
            ".avi, .mkv …). Check that the file is not corrupted and that the path "
            "contains no special characters."
        )

        _heading(card, "!play returns nothing")
        _body(card,
            "yt-dlp requires an internet connection to search YouTube. Check your "
            "connection. If a specific query keeps failing, try a more specific title + artist."
        )

        _heading(card, "Hosts file not written")
        _body(card,
            "If the UAC prompt was declined, open  Notepad  as Administrator, navigate "
            "to  C:\\Windows\\System32\\drivers\\etc\\hosts  and add this line manually:"
        )
        _code(card, "127.0.0.1    entity.tls")

        _heading(card, "Colors not updating in overlay")
        _body(card,
            "Click  Save Settings  in the Features section — colors are pushed to the "
            "overlay only on save, not on picker change."
        )

        _heading(card, "App closes immediately / won't start")
        _body(card,
            "Check that ports 8765 and 8766 are not already in use by another process. "
            "Also make sure  %APPDATA%\\EntityTLS\\entity_config.json  is valid JSON."
        )
