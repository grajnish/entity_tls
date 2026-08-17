import datetime
import urllib.parse
from pathlib import Path

import app.state as state
from app.config import get_video
from app.constants import OVERLAY_HTTP_PORT
from app.server import broadcast


def play_via_browser(path, app):
    if not path:
        app.log("No video path for this tier — skipping", "warn")
        return
    if not state._overlay_connected:
        app.log("SERVER NOT CONNECTED — click Start Server first", "warn")
        return
    if not state._ws_clients:
        app.log("No browser connected — open the overlay URL in TikTok Live Studio", "warn")
        return

    name = Path(path).name
    app.log(f"▶  {name}", "play")
    app.set_playing(name)

    url = f"http://127.0.0.1:{OVERLAY_HTTP_PORT}/asset?p={urllib.parse.quote(path, safe='')}"
    state._play_done.clear()
    broadcast({"type": "jj_video", "play": url})

    state._play_done.wait(timeout=60)
    state.videos_played += 1
    ts = datetime.datetime.now().strftime("%H:%M")
    state._recent_playbacks.insert(0, (ts, name))
    del state._recent_playbacks[20:]
    app.increment_videos_played()
    app.log("✔  Finished", "ok")
    app.set_playing(None)


def video_worker(app):
    while True:
        path = state.video_queue.get()
        app.refresh_stats()
        try:
            play_via_browser(path, app)
        except Exception as e:
            app.log(f"Worker error: {e}", "error")
        state.video_queue.task_done()
        app.refresh_stats()


def _handle_gift(coins, count, app, username="", raw_coins=0, original_coins=0, gift_icon=""):
    if coins <= 0:  # effective=0 means below video threshold
        return
    path = get_video(coins)
    if not path:
        app.log(f"No video for {coins}c tier — skipping", "warn")
        return
    app.log(f"Queued  {count}×  {Path(path).name}  ({coins}c)", "info")
    for _ in range(count):
        state.video_queue.put(path)
    app.refresh_stats()


# auto-register when module is imported
state.gift_handlers.append(_handle_gift)
