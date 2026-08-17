import app.state as state
from app.server import broadcast

_TOP_COUNT = 5


def _sorted_leaderboard():
    ranked = sorted(state.gift_leaderboard.items(), key=lambda x: x[1], reverse=True)[:_TOP_COUNT]
    return [{"rank": i + 1, "name": n, "coins": c, "avatar": state.avatars.get(n, "")} for i, (n, c) in enumerate(ranked)]


def broadcast_leaderboard():
    u_color = state.config.get("gift_leaderboard_username_color", "#ffffff")
    r_color = state.config.get("gift_leaderboard_rank_color",     "#ffffff")
    broadcast({
        "type":           "gift_leaderboard",
        "username_color": u_color,
        "rank_color":     r_color,
        "leaderboard":    _sorted_leaderboard(),
    })


def _handle_gift(coins, count, app, username="", raw_coins=0, original_coins=0, gift_icon=""):
    if not username:
        return
    state.gift_leaderboard[username] = state.gift_leaderboard.get(username, 0) + raw_coins
    broadcast_leaderboard()
    app.refresh_gift_leaderboard()


state.gift_handlers.append(_handle_gift)
