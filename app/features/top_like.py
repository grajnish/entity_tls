import app.state as state
from app.server import broadcast

_TOP_COUNT = 5


def _sorted_leaderboard():
    ranked = sorted(state.top_likes.items(), key=lambda x: x[1], reverse=True)[:_TOP_COUNT]
    return [{"rank": i + 1, "name": n, "likes": c, "avatar": state.avatars.get(n, "")} for i, (n, c) in enumerate(ranked)]


def broadcast_leaderboard():
    u_color = state.config.get("top_like_username_color", "#ffffff")
    broadcast({
        "type":           "top_like",
        "username_color": u_color,
        "leaderboard":    _sorted_leaderboard(),
    })


def _handle_like(like_count, app, username=""):
    if not username:
        return
    state.top_likes[username] = state.top_likes.get(username, 0) + like_count
    broadcast_leaderboard()
    app.refresh_top_likes()


state.like_handlers.append(_handle_like)
