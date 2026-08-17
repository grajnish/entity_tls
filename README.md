# ENTITY TLS

**ENTITY TLS** is a Windows desktop application for TikTok Live streamers. It connects to your TikTok LIVE session in real time and powers interactive overlays for OBS/TikTok Live Studio — including gift leaderboards, top likers, gift rain effects, a music player, and video playback triggered by viewer gifts.

---

## ✨ Features

| Feature | Description |
|---|---|
| 🎬 **JJ Video** | Play videos automatically when viewers send gifts, tiered by coin value |
| 🏆 **Gift Leaderboard** | Live ranking of top gifters in the current session |
| 👑 **Top Gift** | Highlights the single biggest gift sender |
| ❤️ **Top Like** | Tracks and displays the top likers |
| 🌧️ **Gift Rain** | Animated gift icon rain overlay triggered by gifts |
| 🎵 **Music Player** | Comment-controlled music queue overlay |

All overlays are served as local HTML pages (via a built-in HTTP + WebSocket server) and can be added as **Browser Sources** in OBS or **LINK Sources** in TikTok Live Studio.

---

## 🖥️ Requirements

- **Windows 10 / 11** (64-bit)
- **Python 3.11+**
- An active **TikTok LIVE** session (you must be live to connect)

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/grajnish/entity_tls.git
cd entity_tls
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the app

```bash
python entity.py
```

> The app enforces a **single instance** — if ENTITY TLS is already running, it will show a warning and exit.

---

## ⚙️ Configuration

On first launch, a config file is created at:

```
%APPDATA%\EntityTLS\entity_config.json
```

You can configure the following from the **Settings** tab inside the app:

- **TikTok Username** — your `@username` to connect to your live
- **Gift Tiers** — map coin thresholds (10, 20, 30, 100 … 2000) to video files
- **Default Video** — fallback video when no tier matches
- **Music Folder** — folder for the music player queue
- **Overlay Colors** — customize leaderboard/overlay text colors
- **Gift Rain** — toggle, speed, size, max drops, drift, and spawn zone

---

## 🌐 Overlay URLs

Once the server is started from the Dashboard, add these as Browser/LINK Sources:

| Overlay | URL |
|---|---|
| JJ Video | `http://entity.tls:8765/overlay/jj-video` |
| Gift Leaderboard | `http://entity.tls:8765/overlay/gift-leaderboard` |
| Top Like | `http://entity.tls:8765/overlay/top-like` |
| Top Gift | `http://entity.tls:8765/overlay/top-gift` |
| Music Player | `http://entity.tls:8765/overlay/music-player` |
| Gift Rain | `http://entity.tls:8765/overlay/gift-rain` |

> The HTTP server runs on port **8765** and the WebSocket server on port **8766**.

---

## 🗂️ Project Structure

```
entity_tls/
├── entity.py               # Entry point (single-instance guard)
├── app/
│   ├── app.py              # Main application window (CustomTkinter)
│   ├── server.py           # HTTP + WebSocket overlay server
│   ├── tiktok.py           # TikTok Live client & event handlers
│   ├── config.py           # Config load/save/tier resolution
│   ├── constants.py        # App constants, theme colors, default config
│   ├── state.py            # Shared runtime state
│   ├── widgets.py          # Reusable UI helpers
│   ├── loader.py           # Splash screen
│   ├── features/           # Live feature logic
│   │   ├── comment_player.py
│   │   ├── gift_leaderboard.py
│   │   ├── gift_rain.py
│   │   ├── jj_video.py
│   │   ├── top_gift.py
│   │   └── top_like.py
│   ├── tabs/               # UI tab pages
│   │   ├── dashboard/
│   │   ├── features/
│   │   ├── settings/
│   │   ├── log/
│   │   └── tutorial/
│   └── overlays/           # HTML overlay files (served via HTTP)
```

---

## 📦 Building an Executable

To package as a standalone `.exe` (no Python required on target machine):

```bash
pip install pyinstaller
pyinstaller --noconfirm --onefile --windowed --icon=entity-icon.ico entity.py
```

The output will be in the `dist/` folder.

---

## 📄 License

This project is currently unlicensed. All rights reserved.
