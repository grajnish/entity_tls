import customtkinter as ctk

from app.constants import C_ACCENT, C_ACCENTL, C_BORDER, C_MUTED
from app.tabs.features.jj_video_section import JJVideoSection
from app.tabs.features.gift_leaderboard_section import GiftLeaderboardSection
from app.tabs.features.top_like_section import TopLikeSection
from app.tabs.features.top_gift_section import TopGiftSection
from app.tabs.features.music_player_section import MusicPlayerSection
from app.tabs.features.gift_rain_section import GiftRainSection
from app.widgets import make_card, make_label


class FeaturesPage(ctk.CTkFrame):
    def __init__(self, parent, app):
        super().__init__(parent, fg_color="transparent")
        self.app = app
        self._build()

    def _build(self):
        hdr = ctk.CTkFrame(self, fg_color="transparent")
        hdr.pack(fill="x", pady=(0, 14))
        make_label(hdr, "Features", 15, bold=True).pack(side="left")
        ctk.CTkButton(
            hdr, text="\u21ba  Reload", width=90, height=30, corner_radius=8,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 11),
            command=self._reload,
        ).pack(side="right")

        self._scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self._scroll.pack(fill="both", expand=True)
        self._build_sections()

    def _reload(self):
        """Destroy and rebuild all sections so they re-read from state.config."""
        for w in self._scroll.winfo_children():
            w.destroy()
        self._build_sections()

    def _build_sections(self):
        self._add_section(
            self._scroll,
            title="\ud83c\udfa5  JJ VIDEO",
            subtitle="Auto-play a video when viewers send a gift.",
            SectionClass=JJVideoSection,
        )
        self._add_section(
            self._scroll,
            title="\ud83c\udfc6  GIFT LEADERBOARD",
            subtitle="Displays a live diamond leaderboard for your LIVE.",
            SectionClass=GiftLeaderboardSection,
        )
        self._add_section(
            self._scroll,
            title="\u2764\ufe0f  TOP LIKE",
            subtitle="Highlight the viewers sending the most likes.",
            SectionClass=TopLikeSection,
        )
        self._add_section(
            self._scroll,
            title="\ud83d\udc51  TOP GIFT",
            subtitle="Show whoever landed the single biggest gift this session.",
            SectionClass=TopGiftSection,
        )
        self._add_section(
            self._scroll,
            title="\ud83c\udfb5  MUSIC PLAYER",
            subtitle="Let viewers request songs via !play in chat \u2014 plays on your overlay.",
            SectionClass=MusicPlayerSection,
        )
        self._add_section(
            self._scroll,
            title="\ud83c\udf27\ufe0f  GIFT RAIN",
            subtitle="Gift images rain down from the top whenever a viewer sends a gift.",
            SectionClass=GiftRainSection,
        )

    def _add_section(self, parent, title, subtitle, SectionClass):
        card = make_card(parent)
        card.pack(fill="x", pady=(0, 14))

        make_label(card, title, 12, bold=True, color=C_ACCENTL).pack(
            anchor="w", padx=16, pady=(10, 2)
        )
        if subtitle:
            make_label(card, subtitle, 10, color=C_MUTED).pack(
                anchor="w", padx=16, pady=(0, 4)
            )

        ctk.CTkFrame(card, fg_color=C_BORDER, height=1).pack(fill="x", padx=12, pady=(0, 4))

        SectionClass(card, self.app).pack(fill="x")

