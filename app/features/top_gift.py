import app.state as state
from app.server import broadcast


def _broadcast(live=False):
    title   = state.config.get("top_gift_title",          "👑 Top Gift")
    t_color = state.config.get("top_gift_title_color",    "#ffffff")
    u_color = state.config.get("top_gift_username_color", "#ffd700")
    broadcast({
        "type":           "top_gift",
        "title":          title,
        "title_color":    t_color,
        "username_color": u_color,
        "username":       state.top_gift.get("username", ""),
        "coins":          state.top_gift.get("coins", 0),
        "avatar":         state.top_gift.get("avatar", ""),
        "gift_icon":      state.top_gift.get("gift_icon", ""),
        "live":           live,
    })


def broadcast_record():
    _broadcast(live=False)


def _handle_gift(effective, play_count, app, username="", raw_coins=0, original_coins=0, gift_icon=""):
    if not username or original_coins <= 0:
        return
    if original_coins > state.top_gift.get("coins", 0):
        state.top_gift["username"] = username
        state.top_gift["coins"]    = original_coins
        state.top_gift["avatar"]   = state.avatars.get(username, "")
        state.top_gift["gift_icon"] = gift_icon
        _broadcast(live=True)
        app.refresh_top_gift()


state.gift_handlers.append(_handle_gift)
