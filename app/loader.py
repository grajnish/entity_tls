import ctypes
import os
import subprocess
import tempfile
import threading
import time

from app.widgets import set_icon

import customtkinter as ctk

from app.constants import (
    APP_NAME, VERSION,
    C_BG, C_ACCENT, C_ACCENTL, C_GREEN, C_RED, C_YELLOW,
    C_TEXT, C_MUTED, C_BORDER, C_CARD,
)

# ── Hosts file helpers ────────────────────────────────────────────────────────

_HOSTS_PATH  = r"C:\Windows\System32\drivers\etc\hosts"
_HOSTS_HOST  = "entity.tls"
_HOSTS_ENTRY = f"127.0.0.1    {_HOSTS_HOST}"


def _hosts_ok():
    try:
        with open(_HOSTS_PATH, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2 and parts[1] == _HOSTS_HOST:
                    return True
    except OSError:
        pass
    return False


def _write_direct():
    try:
        with open(_HOSTS_PATH, "a", encoding="utf-8") as f:
            f.write(f"\n{_HOSTS_ENTRY}\n")
        return True
    except PermissionError:
        return False


def _is_admin():
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except Exception:
        return False


def _write_elevated():
    """Write a temp .ps1 and run it elevated — avoids all shell-quoting issues."""
    script = (
        f"$h = '{_HOSTS_PATH}'\n"
        f"$e = '{_HOSTS_ENTRY}'\n"
        f"if (-not (Select-String -Path $h -Pattern '{_HOSTS_HOST}' -Quiet)) {{\n"
        f"    [System.IO.File]::AppendAllText($h, [System.Environment]::NewLine + $e)\n"
        f"}}\n"
    )
    fd, ps_path = tempfile.mkstemp(suffix=".ps1")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(script)
        rc = ctypes.windll.shell32.ShellExecuteW(
            None, "runas", "powershell.exe",
            f'-NoProfile -NonInteractive -WindowStyle Hidden -ExecutionPolicy Bypass -File "{ps_path}"',
            None, 0,
        )
        return rc > 32, ps_path
    except Exception:
        try:
            os.unlink(ps_path)
        except OSError:
            pass
        return False, None


def ensure_hosts(status_cb):
    """Check and add entity.tls hosts entry. Returns (ok, detail_str)."""
    if _hosts_ok():
        return True, "Host entry already configured"

    status_cb("Writing host entry…")

    if _is_admin() and _write_direct():
        return True, "Host entry added"

    # Request elevation via a temp .ps1 file
    status_cb("Requesting administrator access…")
    launched, ps_path = _write_elevated()

    if not launched:
        return False, "Elevation cancelled or unavailable"

    # Poll until verified (max 15 s)
    status_cb("Waiting for host entry to be written…")
    result = False, "Could not verify — add manually if needed"
    for _ in range(30):
        time.sleep(0.5)
        if _hosts_ok():
            result = True, "Host entry added (elevated)"
            break

    if ps_path:
        try:
            os.unlink(ps_path)
        except OSError:
            pass

    return result


# ── Splash screen ─────────────────────────────────────────────────────────────

_STEPS = [
    "Loading configuration",
    "Verifying overlay host routing",
    "Checking TikTok LIVE Studio",
    "Initializing feature modules",
    "Building interface",
]


def _tls_running():
    try:
        r = subprocess.run(
            ["tasklist", "/FI", "IMAGENAME eq TikTok LIVE Studio.exe", "/NH"],
            capture_output=True, text=True, creationflags=0x08000000,
        )
        return "TikTok LIVE Studio.exe" in r.stdout
    except Exception:
        return True  # can't check — assume running

_PULSE = ("◌", "◎")


def _work_area():
    """Return (x, y, w, h) of the primary monitor work area (excludes taskbar)."""
    class _RECT(ctypes.Structure):
        _fields_ = [("left", ctypes.c_long), ("top",  ctypes.c_long),
                    ("right",ctypes.c_long), ("bottom",ctypes.c_long)]
    r = _RECT()
    ctypes.windll.user32.SystemParametersInfoW(48, 0, ctypes.byref(r), 0)
    return r.left, r.top, r.right - r.left, r.bottom - r.top


class SplashScreen(ctk.CTkToplevel):
    """
    Professional init splash shown while App is still withdrawn.
    Calls self.on_done() (set by caller) when all steps complete.
    """

    on_done = None  # caller must assign before mainloop

    def __init__(self, parent):
        super().__init__(parent)

        self.overrideredirect(True)
        self.configure(fg_color=C_ACCENT)   # thin accent border via 1 px inset
        self.resizable(False, False)
        self.attributes("-topmost", True)
        set_icon(self)

        w, h = 520, 400
        self.geometry(f"{w}x{h}")

        self._step_icons  = []   # list of (icon_lbl, text_lbl)
        self._step_states = ["pending"] * len(_STEPS)
        self._progress    = ctk.DoubleVar(value=0.0)
        self._status_var  = ctk.StringVar(value="Starting…")

        inner = ctk.CTkFrame(self, fg_color=C_BG, corner_radius=0)
        inner.pack(fill="both", expand=True, padx=1, pady=1)
        self._build(inner)

        # center on work area (excludes taskbar) using fixed known size
        wx, wy, ww, wh = _work_area()
        sx = wx + (ww - w) // 2
        sy = wy + (wh - h) // 2
        self.geometry(f"{w}x{h}+{sx}+{sy}")

        self.after(250, self._start)

    # ── UI construction ───────────────────────────────────────────────────────

    def _build(self, parent):
        # header
        hdr = ctk.CTkFrame(parent, fg_color="transparent")
        hdr.pack(fill="x", padx=32, pady=(28, 0))
        ctk.CTkLabel(
            hdr, text=APP_NAME,
            font=ctk.CTkFont("Segoe UI", 26, "bold"),
            text_color=C_TEXT,
        ).pack(anchor="w")
        ctk.CTkLabel(
            hdr, text=f"v{VERSION}  —  Initializing",
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=C_MUTED,
        ).pack(anchor="w", pady=(2, 0))

        ctk.CTkFrame(parent, fg_color=C_BORDER, height=1).pack(
            fill="x", padx=32, pady=(14, 16),
        )

        # steps
        steps_frame = ctk.CTkFrame(parent, fg_color="transparent")
        steps_frame.pack(fill="x", padx=32)
        for label in _STEPS:
            row = ctk.CTkFrame(steps_frame, fg_color="transparent")
            row.pack(fill="x", pady=4)
            icon_lbl = ctk.CTkLabel(
                row, text="○", width=18,
                font=ctk.CTkFont("Segoe UI", 13),
                text_color="#2a2a50", anchor="w",
            )
            icon_lbl.pack(side="left")
            text_lbl = ctk.CTkLabel(
                row, text=label,
                font=ctk.CTkFont("Segoe UI", 12),
                text_color=C_MUTED, anchor="w",
            )
            text_lbl.pack(side="left", padx=(10, 0))
            self._step_icons.append((icon_lbl, text_lbl))

        # progress bar
        prog_frame = ctk.CTkFrame(parent, fg_color="transparent")
        prog_frame.pack(fill="x", padx=32, pady=(22, 5))
        ctk.CTkProgressBar(
            prog_frame,
            variable=self._progress,
            height=3, corner_radius=2,
            fg_color=C_BORDER, progress_color=C_ACCENT,
        ).pack(fill="x")

        # status text
        ctk.CTkLabel(
            parent,
            textvariable=self._status_var,
            font=ctk.CTkFont("Segoe UI", 10),
            text_color=C_MUTED,
        ).pack(anchor="w", padx=32)

    # ── Step state management ─────────────────────────────────────────────────

    def _set_step(self, idx, state, detail=""):
        """Thread-safe step update."""
        self.after(0, self._apply_step, idx, state, detail)

    def _apply_step(self, idx, state, detail):
        self._step_states[idx] = state
        icon_lbl, text_lbl = self._step_icons[idx]
        if state == "active":
            icon_lbl.configure(text=_PULSE[0], text_color=C_ACCENT)
            text_lbl.configure(text_color=C_TEXT)
            self._pulse(idx, 0)
        elif state == "done":
            icon_lbl.configure(text="✓", text_color=C_GREEN)
            text_lbl.configure(text_color=C_MUTED)
        elif state == "warning":
            icon_lbl.configure(text="⚠", text_color=C_YELLOW)
            text_lbl.configure(text_color=C_YELLOW)
        elif state == "error":
            icon_lbl.configure(text="✗", text_color=C_RED)
            text_lbl.configure(text_color=C_RED)
        done = sum(1 for s in self._step_states if s in ("done", "warning", "error"))
        self._progress.set(done / len(_STEPS))
        if detail:
            self._status_var.set(detail)

    def _pulse(self, idx, frame):
        if self._step_states[idx] != "active":
            return
        self._step_icons[idx][0].configure(text=_PULSE[frame % 2])
        self.after(380, self._pulse, idx, frame + 1)

    def _set_status(self, msg):
        self.after(0, self._status_var.set, msg)

    # ── Init sequence (runs in background thread) ─────────────────────────────

    def _start(self):
        threading.Thread(target=self._run, daemon=True).start()

    def _run(self):
        # ── Step 0: load config
        self._set_step(0, "active")
        self._set_status("Loading configuration…")
        from app.config import load_config
        load_config()
        time.sleep(0.2)
        self._set_step(0, "done", "Configuration loaded")

        # ── Step 1: hosts file
        self._set_step(1, "active")
        self._set_status("Checking overlay host routing…")
        ok, detail = ensure_hosts(self._set_status)
        self._set_step(1, "done" if ok else "warning", detail)

        # ── Step 2: TikTok LIVE Studio
        self._set_step(2, "active")
        self._set_status("Checking TikTok LIVE Studio…")
        if not _tls_running():
            self._set_step(2, "warning", "TikTok LIVE Studio not detected")
            evt = threading.Event()
            go = [True]
            self.after(0, self._show_studio_warning, evt, go)
            evt.wait()
            if not go[0]:
                self.after(0, lambda: os._exit(0))
                return
        else:
            self._set_step(2, "done", "TikTok LIVE Studio is running")

        # ── Step 3: feature modules
        self._set_step(3, "active")
        self._set_status("Loading feature modules…")
        import app.features.jj_video            # noqa: F401
        import app.features.gift_leaderboard    # noqa: F401
        import app.features.top_like            # noqa: F401
        import app.features.top_gift            # noqa: F401
        import app.features.comment_player      # noqa: F401
        import app.features.gift_rain           # noqa: F401
        time.sleep(0.15)
        self._set_step(3, "done", "All modules registered")

        # ── Step 4: build interface
        self._set_step(4, "active")
        self._set_status("Building interface…")
        time.sleep(0.35)
        self._set_step(4, "done", "Ready")

        time.sleep(0.45)
        self.after(0, self._finish)

    def _finish(self):
        self.destroy()
        if callable(self.on_done):
            self.on_done()

    def _show_studio_warning(self, evt, go):
        modal = ctk.CTkToplevel(self)
        modal.overrideredirect(True)
        modal.geometry("420x210")
        modal.configure(fg_color=C_BG)
        modal.attributes("-topmost", True)
        modal.grab_set()
        set_icon(modal)
        wx, wy, ww, wh = _work_area()
        px = wx + (ww - 420) // 2
        py = wy + (wh - 210) // 2
        modal.geometry(f"420x210+{px}+{py}")

        ctk.CTkLabel(
            modal, text="⚠  TikTok LIVE Studio Not Detected",
            font=ctk.CTkFont("Segoe UI", 14, "bold"), text_color=C_YELLOW,
        ).pack(pady=(22, 6))
        ctk.CTkLabel(
            modal,
            text="TikTok LIVE Studio does not appear to be running.\n"
                 "Overlay links will not display until it is launched.",
            font=ctk.CTkFont("Segoe UI", 11), text_color=C_MUTED, justify="center",
        ).pack(pady=(0, 20))

        btn_row = ctk.CTkFrame(modal, fg_color="transparent")
        btn_row.pack(fill="x", padx=24)

        def _continue():
            go[0] = True
            modal.destroy()
            evt.set()

        def _exit():
            go[0] = False
            modal.destroy()
            evt.set()

        ctk.CTkButton(
            btn_row, text="Continue Anyway", height=36,
            fg_color=C_ACCENT, hover_color=C_ACCENTL,
            font=ctk.CTkFont("Segoe UI", 12), command=_continue,
        ).pack(side="left", expand=True, padx=(0, 6))
        ctk.CTkButton(
            btn_row, text="Exit", height=36,
            fg_color="#2a1010", hover_color=C_RED, text_color=C_TEXT,
            font=ctk.CTkFont("Segoe UI", 12), command=_exit,
        ).pack(side="right", expand=True, padx=(6, 0))
