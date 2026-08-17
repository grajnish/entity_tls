import ctypes
import sys

from app.app import App

_MUTEX_NAME = "Global\\EntityTLS_SingleInstance"

if __name__ == "__main__":
    # Prevent multiple instances via a named Windows mutex
    mutex = ctypes.windll.kernel32.CreateMutexW(None, True, _MUTEX_NAME)
    if ctypes.windll.kernel32.GetLastError() == 183:  # ERROR_ALREADY_EXISTS
        ctypes.windll.user32.MessageBoxW(
            None,
            "ENTITY TLS is already running.\n\nCheck the system tray or taskbar.",
            "Already Running",
            0x30,  # MB_ICONWARNING
        )
        sys.exit(0)

    app = App()
    app.mainloop()
    ctypes.windll.kernel32.ReleaseMutex(mutex)
