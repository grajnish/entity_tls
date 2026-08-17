import glob
import os
import shutil
import tempfile
import threading
import time
import urllib.parse

import app.state as state
from app.server import broadcast
from app.constants import OVERLAY_HTTP_PORT

_LOCK = threading.Lock()
_MAX_QUEUE = 10
_TEMP_DIR = tempfile.mkdtemp(prefix="jjlive_music_")
_track_id = 0
_MAX_RETRIES = 5

# Clean up temp dirs from previous sessions on startup
def _cleanup_old_sessions():
    for d in glob.glob(os.path.join(tempfile.gettempdir(), "jjlive_music_*")):
        if d != _TEMP_DIR:
            try:
                shutil.rmtree(d, ignore_errors=True)
            except Exception:
                pass

threading.Thread(target=_cleanup_old_sessions, daemon=True).start()


def _broadcast():
    def _q(i):
        info = i.get("info")
        thumb = (info["thumbnail"] if info else None) or i.get("_thumbnail", "")
        searching = i.get("_preloading") and "info" not in i
        failed = i.get("_failed", False)
        return {
            "query":     i.get("_resolved_title") or i["query"],
            "requester": i["requester"],
            "thumbnail": thumb,
            "searching": searching,
            "failed":    failed,
        }
    broadcast({
        "type":   "music_player",
        "now":    dict(state.music_current),
        "queue":  [_q(i) for i in state.music_display_queue],
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
    })


def send_control(action: str, **kwargs):
    msg = {"type": "music_control", "action": action}
    msg.update(kwargs)
    broadcast(msg)


def _download_audio(query: str):
    global _track_id
    with _LOCK:
        _track_id += 1
        tid = _track_id

    app_ref = state._app_ref
    for attempt in range(_MAX_RETRIES):
        try:
            import yt_dlp
            out_tmpl = os.path.join(_TEMP_DIR, f"track_{tid}.%(ext)s")
            opts = {
                "quiet": True,
                "no_warnings": True,
                "noplaylist": True,
                "format": "bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio[acodec!=none][vcodec=none]/bestaudio",
                "outtmpl": out_tmpl,
            }
            with yt_dlp.YoutubeDL(opts) as ydl:
                raw = ydl.extract_info(f"ytsearch1:{query}", download=True)

            if not raw:
                raise ValueError("no result")
            entries = raw.get("entries")
            entry = entries[0] if entries else raw
            if not entry:
                raise ValueError("no entry")

            vid_id = entry.get("id", "")
            file_path = None
            for fname in os.listdir(_TEMP_DIR):
                if fname.startswith(f"track_{tid}.") and not fname.endswith(".part"):
                    file_path = os.path.join(_TEMP_DIR, fname)
                    break
            if not file_path or not os.path.exists(file_path):
                raise FileNotFoundError("file not found after download")

            encoded = urllib.parse.quote(file_path, safe="")
            return {
                "audioUrl":  f"http://127.0.0.1:{OVERLAY_HTTP_PORT}/asset?p={encoded}",
                "title":     entry.get("title") or query,
                "artist":    entry.get("uploader") or entry.get("channel") or "",
                "thumbnail": f"https://i.ytimg.com/vi/{vid_id}/hqdefault.jpg" if vid_id else "",
            }
        except Exception as exc:
            is_last = attempt == _MAX_RETRIES - 1
            if app_ref:
                if is_last:
                    app_ref.log(f"[!play] Failed after {_MAX_RETRIES} attempts '{query}': {exc}", "error")
                else:
                    app_ref.log(f"[!play] Attempt {attempt + 1}/{_MAX_RETRIES} failed, retrying: {exc}", "warn")
            if not is_last:
                time.sleep(2 ** attempt)  # 1 → 2 → 4 → 8 s
    return None


def _start_download(item: dict):
    """Kick off an immediate download for any queue item, with retry."""
    with _LOCK:
        if item.get("_preloading") or "info" in item:
            return
        item["_preloading"] = True
        evt = threading.Event()
        item["_event"] = evt

    def _do():
        info = _download_audio(item["query"])
        with _LOCK:
            item["info"] = info
            if info:
                item["_resolved_title"] = info["title"]
                item["_thumbnail"] = info["thumbnail"]
            else:
                item["_failed"] = True
        evt.set()
        _broadcast()
        if not info:
            # show "Song not found" briefly, then drop the row
            time.sleep(3)
            with _LOCK:
                if item in state.music_display_queue:
                    state.music_display_queue.remove(item)
            _broadcast()

    threading.Thread(target=_do, daemon=True).start()


def _play_preloaded(item: dict):
    """Play from pre-downloaded info; fall back to full download on failure."""
    info = item.get("info")
    if info and info.get("audioUrl"):
        state.music_current = {
            "status":    "playing",
            "audioUrl":  info["audioUrl"],
            "title":     info["title"],
            "artist":    info["artist"],
            "thumbnail": info["thumbnail"],
            "requester": item["requester"],
        }
        _broadcast()
        app_ref = state._app_ref
        if app_ref:
            app_ref.log(f"[!play] \u25b6 {info['title']} \u2014 by {item['requester']}", "info")
        # kick off download for the new queue[0]
        if state.music_display_queue:
            _start_download(state.music_display_queue[0])
    else:
        threading.Thread(target=_load_and_play, args=(item,), daemon=True).start()


def _load_and_play(item: dict):
    app  = state._app_ref
    query     = item["query"]
    requester = item["requester"]

    info = _download_audio(query)
    if not info or not info.get("audioUrl"):
        if app:
            app.log(f"[!play] No result for: {query}", "warn")
        with _LOCK:
            state.music_current = {}
            next_item = state.music_display_queue.pop(0) if state.music_display_queue else None
        _broadcast()
        if next_item:
            threading.Thread(target=_load_and_play, args=(next_item,), daemon=True).start()
        return

    state.music_current = {
        "status":    "playing",
        "audioUrl":  info["audioUrl"],
        "title":     info["title"],
        "artist":    info["artist"],
        "thumbnail": info["thumbnail"],
        "requester": requester,
    }
    _broadcast()
    if app:
        app.log(f"[!play] \u25b6 {info['title']} \u2014 by {requester}", "info")
    if state.music_display_queue:
        _start_download(state.music_display_queue[0])


def _cleanup_file(audio_url: str):
    """Delete the local temp file after a track finishes."""
    try:
        qs = urllib.parse.parse_qs(urllib.parse.urlparse(audio_url).query)
        path = urllib.parse.unquote(qs.get("p", [""])[0])
        if path and os.path.isfile(path):
            os.unlink(path)
    except Exception:
        pass


def _on_track_ended():
    with _LOCK:
        ended_url = state.music_current.get("audioUrl", "")
        state.music_current = {}
        next_item = state.music_display_queue.pop(0) if state.music_display_queue else None
        if next_item:
            # always show searching so overlay never goes blank between tracks
            state.music_current = {
                "status":    "searching",
                "title":     next_item.get("_resolved_title") or next_item["query"],
                "requester": next_item["requester"],
            }
    if ended_url:
        threading.Thread(target=_cleanup_file, args=(ended_url,), daemon=True).start()
    _broadcast()
    if not next_item:
        return
    evt = next_item.get("_event")
    if evt and not evt.is_set():
        # pre-download in progress — wait for it then play
        def _wait():
            evt.wait(timeout=120)
            _play_preloaded(next_item)
        threading.Thread(target=_wait, daemon=True).start()
    else:
        _play_preloaded(next_item)


def _handle_comment(text: str, username: str, app, is_mod: bool = False) -> None:
    stripped = text.strip()
    cmd = stripped.lower()

    if cmd == "!skip":
        if is_mod and state.music_current:
            app.log(f"[!skip] {username} skipped the track", "info")
            _on_track_ended()
        return

    if cmd == "!cancel":
        with _LOCK:
            for i in range(len(state.music_display_queue) - 1, -1, -1):
                if state.music_display_queue[i]["requester"] == username:
                    removed = state.music_display_queue.pop(i)
                    app.log(f"[!cancel] {username} cancelled: {removed['query']}", "info")
                    break
            else:
                return
        _broadcast()
        return

    if not cmd.startswith("!play"):
        return
    query = stripped[5:].strip()
    if not query:
        return

    with _LOCK:
        min_coins = state.config.get("music_min_coins", 0)
        if min_coins > 0:
            user_coins = state.gift_leaderboard.get(username, 0)
            if user_coins < min_coins:
                app.log(f"[!play] {username} needs {min_coins} coins to request (has {user_coins})", "warn")
                return
        if len(state.music_display_queue) >= state.config.get("music_max_queue", _MAX_QUEUE):
            app.log(f"[!play] Queue full, ignoring: {query}", "warn")
            return
        idle = not state.music_current
        if idle:
            state.music_current = {"status": "searching", "title": query, "requester": username}
            new_queue_item = None
        else:
            new_queue_item = {"query": query, "requester": username}
            state.music_display_queue.append(new_queue_item)

    if idle:
        _broadcast()
        app.log(f"[!play] {username} requested: {query}", "info")
        threading.Thread(
            target=_load_and_play,
            args=({"query": query, "requester": username},),
            daemon=True,
        ).start()
    else:
        # set _preloading=True before broadcast so overlay shows "Searching song..."
        _start_download(new_queue_item)
        _broadcast()
        app.log(f"[!play] {username} added to queue ({len(state.music_display_queue)}): {query}", "info")


state.music_on_ended = _on_track_ended
state.comment_handlers.append(_handle_comment)


def clear_queue():
    """Wipe the display queue only (current track keeps playing)."""
    with _LOCK:
        state.music_display_queue.clear()
    _broadcast()


def stop_current():
    """Stop the current track and advance to the next queued item."""
    _on_track_ended()


def clear_all():
    """Stop the current track AND wipe the entire queue."""
    with _LOCK:
        ended_url = state.music_current.get("audioUrl", "")
        state.music_current = {}
        state.music_display_queue.clear()
    if ended_url:
        threading.Thread(target=_cleanup_file, args=(ended_url,), daemon=True).start()
    _broadcast()


def remove_queue_item(index: int):
    """Remove a single pending item from the display queue by 0-based index."""
    with _LOCK:
        if 0 <= index < len(state.music_display_queue):
            state.music_display_queue.pop(index)
    _broadcast()

