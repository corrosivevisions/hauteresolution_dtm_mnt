"""External webview management for the ComfyUI UI (Phase A)."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from typing import Optional

try:  # pragma: no cover - optional dependency
    import webview
except Exception:  # pragma: no cover - optional dependency
    webview = None  # type: ignore[assignment]


@dataclass
class WindowBounds:
    x: float
    y: float
    width: float
    height: float


class ExternalWebviewController:
    """Manage a pywebview window pointing to the ComfyUI frontend."""

    def __init__(self) -> None:
        self._window: Optional["webview.Window"] = None
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        self._target_url: Optional[str] = None
        self._always_on_top: bool = True
        self._bounds = WindowBounds(100, 100, 1280, 720)

    # ------------------------------------------------------------------
    def open(self, url: str, *, always_on_top: bool, bounds: WindowBounds) -> None:
        if webview is None:
            raise RuntimeError("pywebview is not available. Install it in Blender's Python environment.")

        with self._lock:
            self._target_url = url
            self._always_on_top = always_on_top
            self._bounds = bounds

            if self._window is not None and self._thread and self._thread.is_alive():
                self._window.load_url(url)
                self._apply_window_state()
                return

            def _run() -> None:
                window = webview.create_window(
                    "ComfyUI",
                    url,
                    x=int(bounds.x),
                    y=int(bounds.y),
                    width=int(bounds.width),
                    height=int(bounds.height),
                    on_top=always_on_top,
                )
                self._window = window
                try:
                    webview.start(self._on_ready, window)
                finally:
                    with self._lock:
                        self._window = None
                        self._thread = None

            thread = threading.Thread(target=_run, daemon=True)
            self._thread = thread
            thread.start()

    def close(self) -> None:
        with self._lock:
            if self._window is not None and webview is not None:
                webview.destroy_window(self._window)
            self._window = None
            self._thread = None

    def focus(self) -> None:
        with self._lock:
            if self._window is not None:
                try:
                    self._window.bring_to_front()
                except AttributeError:  # pragma: no cover - platform dependent
                    pass

    def set_bounds(self, bounds: WindowBounds) -> None:
        with self._lock:
            self._bounds = bounds
            if self._window is not None:
                try:
                    self._window.resize(int(bounds.width), int(bounds.height))
                    self._window.move(int(bounds.x), int(bounds.y))
                except AttributeError:  # pragma: no cover - platform dependent
                    pass

    def is_open(self) -> bool:
        with self._lock:
            if self._window is None:
                return False
            return bool(webview and self._window in webview.windows)

    # ------------------------------------------------------------------
    def _apply_window_state(self) -> None:
        if self._window is None:
            return
        try:
            self._window.on_top = self._always_on_top
        except AttributeError:  # pragma: no cover - platform dependent
            pass

    def _on_ready(self) -> None:
        self._apply_window_state()


_CONTROLLER = ExternalWebviewController()


def get_controller() -> ExternalWebviewController:
    return _CONTROLLER


def register() -> None:  # pragma: no cover - nothing to do
    pass


def unregister() -> None:
    _CONTROLLER.close()
