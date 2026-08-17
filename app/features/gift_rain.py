import app.state as state
from app.server import broadcast


def _handle_gift(coins: int, count: int, gift_icon: str):
    if not state.config.get("gift_rain_enabled", True):
        return
    if not gift_icon:
        return
    actual = max(count, 1)
    max_drops = state.config.get("gift_rain_max_drops", 80)
    broadcast({
        "type":       "gift_rain",
        "image":      gift_icon,
        "count":      min(actual, max_drops),
        "speed":      state.config.get("gift_rain_speed",      "normal"),
        "size":       state.config.get("gift_rain_size",       56),
        "pile":       state.config.get("gift_rain_pile",       True),
        "drift":      state.config.get("gift_rain_drift",      True),
        "spawn_zone": state.config.get("gift_rain_spawn_zone", "full"),
        "max_drops":  max_drops,
    })


state.raw_gift_handlers.append(_handle_gift)
