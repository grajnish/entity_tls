import sys
import os

from app.app import App

def _already_running_warning(message, title):
    """Show a warning dialog using the best available method for the platform."""
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showwarning(title, message)
        root.destroy()
    except Exception:
        print(f"[{title}] {message}", file=sys.stderr)


if sys.platform == "win32":
    import ctypes

    _MUTEX_NAME = "Global\\EntityTLS_SingleInstance"

    def _acquire_lock():
        mutex = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
        if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
            _already_running_warning(
                "ENTITY TLS is already running.\n\nCheck the system tray or taskbar.",
                "Already Running",
            )
            sys.exit(0)
        return mutex

    def _release_lock(handle):
        ctypes.windll.kernel32.ReleaseMutex(handle)

else:
    # Linux / macOS — use a PID lock file in the user's runtime or temp directory
    import atexit
    import tempfile

    _LOCK_FILE = os.path.join(
        os.environ.get("XDG_RUNTIME_DIR") or tempfile.gettempdir(),
        "entity_tls.lock",
    )

    _lock_fd = None

    def _acquire_lock():
        global _lock_fd
        import fcntl
        _lock_fd = open(_LOCK_FILE, "w")
        try:
            fcntl.flock(_lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            _lock_fd.close()
            _already_running_warning(
                "ENTITY TLS is already running.\n\nCheck your taskbar or running processes.",
                "Already Running",
            )
            sys.exit(0)
        _lock_fd.write(str(os.getpid()))
        _lock_fd.flush()
        atexit.register(_release_lock, None)
        return _lock_fd

    def _release_lock(handle):
        global _lock_fd
        import fcntl
        fd = handle or _lock_fd
        if fd:
            try:
                fcntl.flock(fd, fcntl.LOCK_UN)
                fd.close()
            except Exception:
                pass
        try:
            os.remove(_LOCK_FILE)
        except OSError:
            pass


if __name__ == "__main__":
    lock = _acquire_lock()

    app = App()
    app.mainloop()

    _release_lock(lock)
