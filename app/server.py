import asyncio
import json
import mimetypes
import os
import socketserver
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from threading import Lock, Thread

_ALLOWED_ASSET_EXTS = {
    '.mp4', '.mov', '.avi', '.mkv', '.wmv', '.flv', '.m4v', '.ts', '.webm',
    '.m4a', '.mp3', '.ogg', '.opus', '.flac', '.wav', '.aac',
    '.jpg', '.jpeg', '.png', '.webp', '.gif',
}

import websockets

import app.state as state
from app.constants import OVERLAY_HTTP_PORT, OVERLAY_WS_PORT

_music_current_lock = Lock()

_OVERLAYS = Path(__file__).parent / "overlays"

# Cache of allowed base directories, rebuilt when the server is started or config is saved.
_allowed_bases_cache: list[str] = []


def refresh_allowed_bases():
    """Rebuild the cached list of directories that asset serving is allowed from.

    Call this once when the overlay server starts and again whenever the user
    saves settings (so newly configured video/music paths are picked up without
    a restart).
    """
    bases: list[str] = []
    folder = state.config.get("music_folder", "")
    if folder:
        try:
            bases.append(os.path.realpath(folder) + os.sep)
        except Exception:
            pass
    # Parent directories of all configured video tier paths
    tiers = state.config.get("tiers", {})
    for paths in tiers.values():
        if isinstance(paths, list):
            for p in paths:
                if p:
                    try:
                        bases.append(os.path.realpath(os.path.dirname(p)) + os.sep)
                    except Exception:
                        pass
    for p in state.config.get("default_video", []):
        if p:
            try:
                bases.append(os.path.realpath(os.path.dirname(p)) + os.sep)
            except Exception:
                pass
    global _allowed_bases_cache
    _allowed_bases_cache = bases


def _get_allowed_bases() -> list[str]:
    """Return the cached list of allowed base directories."""
    return _allowed_bases_cache


class _ThreadHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    daemon_threads = True


class _OverlayHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path in ('/', '/overlay/jj-video'):
            self._serve_html((_OVERLAYS / "jj_video.html").read_bytes())
        elif parsed.path == '/overlay/gift-leaderboard':
            self._serve_html((_OVERLAYS / "gift_leaderboard.html").read_bytes())
        elif parsed.path == '/overlay/top-like':
            self._serve_html((_OVERLAYS / "top_like.html").read_bytes())
        elif parsed.path == '/overlay/top-gift':
            self._serve_html((_OVERLAYS / "top_gift.html").read_bytes())
        elif parsed.path == '/overlay/music-player':
            self._serve_html((_OVERLAYS / "music_player.html").read_bytes())
        elif parsed.path == '/overlay/gift-rain':
            self._serve_html((_OVERLAYS / "gift_rain.html").read_bytes())
        elif parsed.path == '/asset':
            qs    = urllib.parse.parse_qs(parsed.query)
            fpath = urllib.parse.unquote(qs.get('p', [''])[0])
            self._serve_file(fpath)
        else:
            self.send_response(404)
            self.end_headers()

    def _serve_html(self, body: bytes):
        self.send_response(200)
        self.send_header('Content-Type', 'text/html; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _serve_file(self, path):
        ext = os.path.splitext(path)[1].lower()
        if not path or ext not in _ALLOWED_ASSET_EXTS:
            self.send_response(404)
            self.end_headers()
            return
        # Resolve to real absolute path and verify it is inside an allowed base directory
        try:
            real = os.path.realpath(path)
        except Exception:
            self.send_response(404)
            self.end_headers()
            return
        allowed_bases = _get_allowed_bases()
        if not any(real.startswith(base) for base in allowed_bases):
            self.send_response(403)
            self.end_headers()
            return
        # `real` is safe to use: extension was checked against _ALLOWED_ASSET_EXTS,
        # the path was canonicalized with os.path.realpath, and confirmed to be
        # under one of the pre-configured allowed base directories above.
        if not os.path.isfile(real):
            self.send_response(404)
            self.end_headers()
            return
        path = real
        size = os.path.getsize(path)
        ct, _  = mimetypes.guess_type(path)
        ct     = ct or 'application/octet-stream'
        rng  = self.headers.get('Range', '')
        try:
            if rng.startswith('bytes='):
                s, e   = rng[6:].split('-')
                start  = int(s)
                end    = int(e) if e else size - 1
                length = end - start + 1
                self.send_response(206)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
                self.send_header('Content-Length', str(length))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                with open(path, 'rb') as f:
                    f.seek(start)
                    rem = length
                    while rem > 0:
                        chunk = f.read(min(65536, rem))
                        if not chunk:
                            break
                        self.wfile.write(chunk)
                        rem -= len(chunk)
            else:
                self.send_response(200)
                self.send_header('Content-Type', ct)
                self.send_header('Content-Length', str(size))
                self.send_header('Accept-Ranges', 'bytes')
                self.end_headers()
                with open(path, 'rb') as f:
                    while True:
                        chunk = f.read(65536)
                        if not chunk:
                            break
                        self.wfile.write(chunk)
        except Exception:
            pass

    def log_message(self, *args):
        pass


async def _ws_handler(websocket):
    state._ws_clients.add(websocket)
    if state._app_ref:
        state._app_ref.set_clients_count(len(state._ws_clients))
    # send current leaderboard so the overlay is correct even if opened after gifts fired
    # always push configured title/colors; include leaderboard data if any gifts exist
    _lb_data = []
    if state.gift_leaderboard:
        ranked = sorted(state.gift_leaderboard.items(), key=lambda x: x[1], reverse=True)[:5]
        _lb_data = [{"rank": i + 1, "name": n, "coins": c, "avatar": state.avatars.get(n, "")} for i, (n, c) in enumerate(ranked)]
    u_color = state.config.get("gift_leaderboard_username_color", "#ffffff")
    r_color = state.config.get("gift_leaderboard_rank_color",     "#ffffff")
    try:
        await websocket.send(json.dumps({
            "type":           "gift_leaderboard",
            "username_color": u_color,
            "rank_color":     r_color,
            "leaderboard":    _lb_data,
        }))
    except Exception:
        pass
    _tl_data = []
    if state.top_likes:
        ranked = sorted(state.top_likes.items(), key=lambda x: x[1], reverse=True)[:5]
        _tl_data = [{"rank": i + 1, "name": n, "likes": c, "avatar": state.avatars.get(n, "")} for i, (n, c) in enumerate(ranked)]
    u_color = state.config.get("top_like_username_color", "#ffffff")
    try:
        await websocket.send(json.dumps({
            "type":           "top_like",
            "username_color": u_color,
            "leaderboard":    _tl_data,
        }))
    except Exception:
        pass
    _tg = state.top_gift or {}
    title   = state.config.get("top_gift_title",          "👑 Top Gift")
    t_color = state.config.get("top_gift_title_color",    "#ffffff")
    u_color = state.config.get("top_gift_username_color", "#ffd700")
    try:
        await websocket.send(json.dumps({
            "type":           "top_gift",
            "title":          title,
            "title_color":    t_color,
            "username_color": u_color,
            "username":       _tg.get("username", ""),
            "coins":          _tg.get("coins", 0),
            "avatar":         _tg.get("avatar", ""),
            "gift_icon":      _tg.get("gift_icon", ""),
            "live":           False,
        }))
    except Exception:
        pass
    # send current music player state on connect
    try:
        with _music_current_lock:
            music_snap = dict(state.music_current)
        await websocket.send(json.dumps({
            "type":   "music_player",
            "now":    music_snap,
            "queue":  [{"query": i.get("_resolved_title") or i["query"], "requester": i["requester"]} for i in state.music_display_queue],
            "volume": state.music_volume,
            "paused": state.music_paused,
            "colors": {
                "song":        state.config.get("music_color_song",        "#ffffff"),
                "artist":      state.config.get("music_color_artist",      "#b4ffeb"),
                "user":        state.config.get("music_color_user",        "#aaaaaa"),
                "queue_label": state.config.get("music_color_queue_label", "#00dcb4"),
                "queue_index": state.config.get("music_color_queue_index", "#00dcb4"),
                "queue_song":  state.config.get("music_color_queue_song",  "#d9d9d9"),
                "queue_by":    state.config.get("music_color_queue_by",    "#595959"),
            },
        }))
    except Exception:
        pass
    try:
        async for raw in websocket:
            try:
                msg = json.loads(raw)
                if msg.get('type') == 'identify':
                    name = msg.get('overlay', '')
                    if name:
                        old = state._ws_by_overlay.get(name)
                        if old and old is not websocket:
                            await old.close()
                        state._ws_by_overlay[name] = websocket
                elif msg.get('type') == 'jj_video' and msg.get('ended'):
                    state._play_done.set()
                elif msg.get('type') == 'music_player' and msg.get('action') == 'ended':
                    cb = getattr(state, 'music_on_ended', None)
                    if callable(cb):
                        cb()
            except Exception:
                pass
    except Exception:
        pass
    finally:
        state._ws_clients.discard(websocket)
        if state._app_ref:
            state._app_ref.set_clients_count(len(state._ws_clients))


async def _ws_serve():
    async with websockets.serve(_ws_handler, '127.0.0.1', OVERLAY_WS_PORT):
        await state._ws_stop_event.wait()  # blocks until stop_overlay_server signals


def _start_ws_thread():
    loop = asyncio.new_event_loop()
    state._ws_loop = loop
    asyncio.set_event_loop(loop)
    state._ws_stop_event = asyncio.Event()
    try:
        loop.run_until_complete(_ws_serve())
    except RuntimeError:
        pass  # suppressed: loop closed on app exit
    finally:
        loop.close()


def broadcast(payload: dict):
    """Send a JSON payload to all connected overlay clients."""
    if not state._ws_loop or not state._ws_clients:
        return
    msg = json.dumps(payload)

    async def _send():
        dead = set()
        for ws in list(state._ws_clients):
            try:
                await ws.send(msg)
            except Exception:
                dead.add(ws)
        if dead:
            state._ws_clients.difference_update(dead)
            if state._app_ref:
                state._app_ref.set_clients_count(len(state._ws_clients))

    asyncio.run_coroutine_threadsafe(_send(), state._ws_loop)


def start_overlay_server(app):
    refresh_allowed_bases()
    try:
        state._http_server = _ThreadHTTPServer(('127.0.0.1', OVERLAY_HTTP_PORT), _OverlayHandler)
    except OSError as e:
        app.log(f"Cannot start HTTP server: {e} — port {OVERLAY_HTTP_PORT} may already be in use.", "error")
        return
    try:
        Thread(target=state._http_server.serve_forever, daemon=True).start()
        Thread(target=_start_ws_thread, daemon=True).start()
    except Exception as e:
        app.log(f"Cannot start overlay server threads: {e}", "error")
        return
    state._overlay_connected = True
    app.set_overlay_status(True)
    app.log("SERVER CONNECTED", "ok")
    app.show_server_modal()


def stop_overlay_server(app):
    if state._http_server:
        state._http_server.shutdown()
        state._http_server = None
    if state._ws_loop and state._ws_stop_event:
        state._ws_loop.call_soon_threadsafe(state._ws_stop_event.set)
    state._ws_stop_event = None
    state._ws_loop = None
    state._ws_clients.clear()
    state._ws_by_overlay.clear()
    state._play_done.set()  # unblock video worker if it's waiting on overlay "ended"
    state._overlay_connected = False
    app.set_overlay_status(False)
    app.log("SERVER STOPPED", "warn")
