import asyncio

from TikTokLive import TikTokLiveClient
from TikTokLive.events import CommentEvent, GiftEvent, LikeEvent

import app.state as state


def _avatar(user):
    try:
        urls = user.avatar_thumb.m_urls
        return urls[0] if urls else ""
    except Exception:
        return ""


def _gift_icon(gift):
    try:
        urls = gift.image.m_urls
        return urls[0] if urls else ""
    except Exception:
        return ""


def handle_like(event: LikeEvent, app):
    username = ""
    if event.user:
        username = getattr(event.user, "nickname", None) or getattr(event.user, "unique_id", "") or ""
        if username:
            state.avatars[username] = _avatar(event.user)
    like_count = getattr(event, "count", 0) or 0
    if like_count <= 0:
        return
    for handler in state.like_handlers:
        handler(like_count, app, username)


def handle_gift(event: GiftEvent, app):
    if not event.repeat_end:
        return

    coins = event.gift.diamond_count
    count = event.repeat_count or 1  # TikTok sends 0 for single non-combo gifts
    gift_icon = _gift_icon(event.gift)

    for handler in state.raw_gift_handlers:
        handler(coins, count, gift_icon)

    if coins < 10:
        total = coins * count
        if total < 10:
            app.log(f"Gift too small for video  ({coins}c \u00d7 {count})  \u2014 total {total}c below minimum tier", "warn")
            effective, play_count = 0, 0
        else:
            effective, play_count = total, 1
    else:
        effective, play_count = coins, count

    username = ""
    if event.user:
        username = getattr(event.user, "nickname", None) or getattr(event.user, "unique_id", "") or ""
        if username:
            state.avatars[username] = _avatar(event.user)

    for handler in state.gift_handlers:
        handler(effective, play_count, app, username, coins * count, coins, gift_icon)


def handle_comment(event: CommentEvent, app):
    text = getattr(event, "comment", None) or getattr(event, "content", None) or ""
    username = ""
    is_mod = False
    if event.user:
        username = getattr(event.user, "nickname", None) or getattr(event.user, "unique_id", "") or ""
        is_mod = bool(getattr(event.user, "is_moderator", False))
        # streamer's own comments also have mod authority
        streamer = state.config.get("username", "").lstrip("@").lower()
        uid = getattr(event.user, "unique_id", "") or ""
        if streamer and uid.lower() == streamer:
            is_mod = True
    for handler in state.comment_handlers:
        handler(text, username, app, is_mod)


def _run_tiktok(app):
    username = state.config.get("username", "")
    if not username:
        app.log("No username set in Settings.", "error")
        app.set_monitoring(False)
        return

    app.log(f"Connecting to TikTok LIVE: {username}", "info")
    state.tiktok_client = TikTokLiveClient(unique_id=username)

    @state.tiktok_client.on(LikeEvent)
    async def on_like(event):
        handle_like(event, app)

    @state.tiktok_client.on(GiftEvent)
    async def on_gift(event):
        handle_gift(event, app)

    @state.tiktok_client.on(CommentEvent)
    async def on_comment(event):
        handle_comment(event, app)

    try:
        state.tiktok_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(state.tiktok_loop)
        app.set_tiktok_status(True)
        app.log("TikTok LIVE monitoring started", "ok")
        state.tiktok_loop.run_until_complete(state.tiktok_client.connect())
    except Exception as e:
        app.log(f"TikTok error: {e}", "error")
    finally:
        app.set_tiktok_status(False)
        app.set_monitoring(False)
        app.log("TikTok LIVE monitoring stopped", "warn")
