"""Cross-platform single-instance guard for Streamer Suite."""

import ctypes
import os
import tempfile


class SingleInstance:
    """Hold an OS-level lock for the lifetime of the application process."""

    WINDOWS_ALREADY_EXISTS = 183

    def __init__(self, name="TDitbamStreamerSuite"):
        self.name = name
        self._handle = None
        self._activation_event = None
        self._lock_file = None

    def acquire(self):
        if os.name == "nt":
            kernel32 = ctypes.windll.kernel32
            kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_wchar_p]
            kernel32.CreateMutexW.restype = ctypes.c_void_p
            self._handle = kernel32.CreateMutexW(None, True, f"Local\\{self.name}.SingleInstance")
            if not self._handle:
                raise ctypes.WinError()
            mutex_already_exists = kernel32.GetLastError() == self.WINDOWS_ALREADY_EXISTS
            kernel32.CreateEventW.argtypes = [ctypes.c_void_p, ctypes.c_bool, ctypes.c_bool, ctypes.c_wchar_p]
            kernel32.CreateEventW.restype = ctypes.c_void_p
            self._activation_event = kernel32.CreateEventW(
                None, False, False, f"Local\\{self.name}.ActivateWindow"
            )
            if mutex_already_exists:
                if self._activation_event:
                    kernel32.SetEvent(self._activation_event)
                    kernel32.CloseHandle(self._activation_event)
                    self._activation_event = None
                kernel32.CloseHandle(self._handle)
                self._handle = None
                return False
            return True

        # The project is Windows-first, but keep development runs on POSIX
        # protected as well.
        import fcntl

        lock_path = os.path.join(tempfile.gettempdir(), f"{self.name}.lock")
        self._lock_file = open(lock_path, "a+")
        try:
            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except BlockingIOError:
            self._lock_file.close()
            self._lock_file = None
            return False

    def activation_requested(self):
        """Consume a request from a duplicate launch to show the main window."""
        if os.name != "nt" or not self._activation_event:
            return False
        return ctypes.windll.kernel32.WaitForSingleObject(self._activation_event, 0) == 0

    def release(self):
        if os.name == "nt" and self._handle:
            ctypes.windll.kernel32.ReleaseMutex(self._handle)
            ctypes.windll.kernel32.CloseHandle(self._handle)
            self._handle = None
            if self._activation_event:
                ctypes.windll.kernel32.CloseHandle(self._activation_event)
                self._activation_event = None
        elif self._lock_file:
            import fcntl

            fcntl.flock(self._lock_file.fileno(), fcntl.LOCK_UN)
            self._lock_file.close()
            self._lock_file = None
