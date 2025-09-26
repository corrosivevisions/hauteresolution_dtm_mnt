"""Process management and logging helpers for the ComfyUI bridge."""
from __future__ import annotations

import queue
import subprocess
import threading
from collections import deque
from dataclasses import dataclass
from pathlib import Path
from typing import Deque, Optional

import bpy
from bpy.app.timers import TimerError
from bpy.props import BoolProperty, StringProperty

from .prefs import ComfyAddonPreferences, get_preferences

LOG_TIMER_INTERVAL = 0.5
STOP_TIMEOUT = 5.0


@dataclass
class LogSnapshot:
    text: str
    line_count: int


class ComfyProcessManager:
    """Manage a ComfyUI subprocess and surface its log output."""

    def __init__(self) -> None:
        self._process: Optional[subprocess.Popen[str]] = None
        self._log_queue: "queue.Queue[str]" = queue.Queue()
        self._log_cache: Deque[str] = deque(maxlen=500)
        self._reader_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._timer_registered: bool = False

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def start(self, prefs: ComfyAddonPreferences) -> None:
        if self.is_running:
            return

        validation = prefs.validate()
        if not validation.ok:
            raise RuntimeError(validation.message)

        python = prefs.resolved_python() or self._auto_python_path()
        if python is None:
            raise RuntimeError("Unable to locate Python executable. Set one in the add-on preferences.")

        comfy_dir = prefs.comfy_path()
        command = [python, "main.py", "--listen", prefs.host, "--port", str(prefs.port)]

        try:
            self._process = subprocess.Popen(
                command,
                cwd=str(comfy_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
        except FileNotFoundError as exc:  # pragma: no cover - defensive
            raise RuntimeError(f"Failed to launch ComfyUI: {exc}") from exc

        self._stop_event.clear()
        self._log_cache = deque(maxlen=prefs.log_history_lines)
        self._reader_thread = threading.Thread(target=self._reader_loop, daemon=True)
        self._reader_thread.start()

        self._set_running_state(True)
        self._ensure_timer()

    def stop(self) -> None:
        if not self.is_running:
            return

        assert self._process is not None
        process = self._process
        self._stop_event.set()

        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=STOP_TIMEOUT)
            except subprocess.TimeoutExpired:
                process.kill()

        if process.stdout is not None:
            process.stdout.close()
        self._process = None
        self._reader_thread = None
        self._set_running_state(False)
        self._cancel_timer()
        self._flush_logs()

    # ------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------
    @property
    def is_running(self) -> bool:
        return self._process is not None and self._process.poll() is None

    # ------------------------------------------------------------------
    # Log access
    # ------------------------------------------------------------------
    def snapshot(self) -> LogSnapshot:
        lines = list(self._log_cache)
        return LogSnapshot("\n".join(lines), len(lines))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _auto_python_path(self) -> Optional[str]:
        return str(Path(bpy.app.binary_path_python)) if bpy.app.binary_path_python else None

    def _reader_loop(self) -> None:
        assert self._process is not None
        if self._process.stdout is None:
            return

        for raw_line in self._process.stdout:
            if self._stop_event.is_set():
                break
            line = raw_line.rstrip("\n")
            self._log_queue.put(line)

        # Drain remaining data
        remaining = self._process.stdout.read()
        if remaining:
            for raw_line in remaining.splitlines():
                self._log_queue.put(raw_line)

    def _ensure_timer(self) -> None:
        if self._timer_registered:
            return
        bpy.app.timers.register(self._flush_logs_timer, first_interval=LOG_TIMER_INTERVAL)
        self._timer_registered = True

    def _cancel_timer(self) -> None:
        if not self._timer_registered:
            return
        try:
            bpy.app.timers.unregister(self._flush_logs_timer)
        except TimerError:
            pass
        finally:
            self._timer_registered = False

    def _flush_logs_timer(self) -> float:
        self._flush_logs()
        return LOG_TIMER_INTERVAL if self.is_running else -1.0

    def _flush_logs(self) -> None:
        prefs = get_preferences()
        target_size = prefs.log_history_lines
        if self._log_cache.maxlen != target_size:
            self._log_cache = deque(self._log_cache, maxlen=target_size)

        changed = False
        while True:
            try:
                line = self._log_queue.get_nowait()
            except queue.Empty:
                break
            self._log_cache.append(line)
            changed = True

        if changed:
            wm = bpy.context.window_manager
            if hasattr(wm, "blender_comfyui_log"):
                wm.blender_comfyui_log = "\n".join(self._log_cache)

    def _set_running_state(self, running: bool) -> None:
        wm = bpy.context.window_manager
        if hasattr(wm, "blender_comfyui_server_running"):
            wm.blender_comfyui_server_running = running


_MANAGER = ComfyProcessManager()


def get_manager() -> ComfyProcessManager:
    return _MANAGER


def register() -> None:
    bpy.types.WindowManager.blender_comfyui_log = StringProperty(
        name="ComfyUI Log", default="", options={"MULTILINE"}
    )
    bpy.types.WindowManager.blender_comfyui_server_running = BoolProperty(
        name="ComfyUI Running", default=False
    )


def unregister() -> None:
    _MANAGER.stop()
    _MANAGER._cancel_timer()
    del bpy.types.WindowManager.blender_comfyui_log
    del bpy.types.WindowManager.blender_comfyui_server_running
