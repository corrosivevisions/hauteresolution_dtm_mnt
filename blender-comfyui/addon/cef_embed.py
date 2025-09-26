"""Placeholder module for Phase B (CEF embedding)."""
from __future__ import annotations

import logging

_LOGGER = logging.getLogger(__name__)


class CefRuntime:
    """Minimal stub describing the future CEF runtime integration."""

    def __init__(self) -> None:
        self.initialised = False

    def initialize(self) -> None:
        _LOGGER.info("CEF embedding is not yet implemented. Phase B will provide this feature.")

    def shutdown(self) -> None:
        _LOGGER.info("CEF embedding shutdown placeholder invoked.")


_RUNTIME = CefRuntime()


def get_runtime() -> CefRuntime:
    return _RUNTIME


def register() -> None:  # pragma: no cover - nothing to register yet
    pass


def unregister() -> None:
    _RUNTIME.shutdown()
