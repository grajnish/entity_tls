from queue import Queue
from threading import Event

config: dict       = {}
video_queue        = Queue()
tiktok_client      = None
tiktok_loop        = None
session_start      = None
videos_played: int = 0

_ws_clients        = set()
_ws_by_overlay     = {}  # overlay name → single active websocket connection
_ws_loop           = None
_ws_stop_event     = None
_http_server       = None
_play_done         = Event()
_overlay_connected = False
_app_ref           = None
_recent_playbacks  = []
gift_handlers: list     = []
raw_gift_handlers: list = []  # called with raw (coins, count, icon) before any coin filtering
like_handlers: list     = []
comment_handlers: list  = []
gift_leaderboard:  dict  = {}  # username → total diamonds this session
top_likes:    dict  = {}  # username → total likes this session
top_gift:     dict  = {}  # {"username": str, "coins": int} — single highest gift event
avatars:      dict  = {}  # username → latest avatar URL (CDN, session-lived)
music_current:       dict  = {}   # {status, videoId, title, artist, thumbnail, requester}
music_display_queue: list  = []   # [{query, requester}, ...]
music_on_ended             = None # callback registered by comment_player
music_volume:  float = 1.0
music_paused:  bool  = False
