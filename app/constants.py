APP_NAME  = "ENTITY TLS"
VERSION   = "1.0.0"

TIER_KEYS = ["10", "20", "30", "100", "200", "300", "500", "1000", "2000"]

TIER_THRESHOLDS = [
    (2000, "2000"), (1000, "1000"), (500,  "500"),
    (299,  "300"),  (199,  "200"),  (99,   "100"),
    (30,   "30"),   (20,   "20"),   (10,   "10"),
]

TIER_COLORS = {
    "10":   "#1a5c38", "20":   "#14506a",
    "30":   "#4a2370", "100":  "#1a5c38",
    "200":  "#14506a", "300":  "#4a2370",
    "500":  "#7a2218", "1000": "#6b5607",
    "2000": "#1a252f",
}

OVERLAY_HTTP_PORT = 8765
OVERLAY_WS_PORT   = 8766

DEFAULT_CONFIG = {
    "username":         "",
    "music_folder":     "",
    "default_video":    [],
    "tiers":            {k: [] for k in TIER_KEYS},
    "gift_leaderboard_username_color": "#ffffff",
    "gift_leaderboard_rank_color":     "#ffd700",
    "top_like_username_color": "#ffffff",
    "top_gift_title":          "👑 Top Gift",
    "top_gift_title_color":    "#ffffff",
    "top_gift_username_color": "#ffd700",
    "gift_rain_enabled":   True,
    "gift_rain_speed":     "normal",
    "gift_rain_size":      56,
    "gift_rain_max_drops": 80,
    "gift_rain_pile":      True,
    "gift_rain_drift":     True,
    "gift_rain_spawn_zone": "full",
}

# ── Theme ─────────────────────────────────────────────────────────────────────
C_BG      = "#080816"
C_SIDEBAR = "#0c0c20"
C_CARD    = "#11112a"
C_CARD2   = "#0e0e24"
C_ACCENT  = "#6c5ce7"
C_ACCENTL = "#a29bfe"
C_GREEN   = "#00b894"
C_RED     = "#d63031"
C_YELLOW  = "#fdcb6e"
C_TEXT    = "#dfe6e9"
C_MUTED   = "#4a4a6a"
C_BORDER  = "#1e1e40"

LOG_COLORS = {
    "ok":    "#00b894", "warn":  "#fdcb6e",
    "error": "#d63031", "info":  "#74b9ff",
    "play":  "#a29bfe",
}
