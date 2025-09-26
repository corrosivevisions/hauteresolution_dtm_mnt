"""Minimal REST helpers for communicating with a ComfyUI server."""
from __future__ import annotations

from typing import Any, Dict, Optional

import requests

from .prefs import ComfyAddonPreferences

DEFAULT_TIMEOUT = 5.0


class ComfyApiError(RuntimeError):
    """Raised when the ComfyUI API returned an unexpected response."""


def _request_json(method: str, url: str, *, timeout: float, json_payload: Optional[Dict[str, Any]] = None) -> Any:
    response = requests.request(method, url, json=json_payload, timeout=timeout)
    response.raise_for_status()
    if not response.content:
        return None
    return response.json()


def system_stats(prefs: ComfyAddonPreferences, timeout: float = DEFAULT_TIMEOUT) -> Dict[str, Any]:
    url = f"{prefs.base_url()}/system_stats"
    data = _request_json("GET", url, timeout=timeout)
    if not isinstance(data, dict):  # pragma: no cover - defensive
        raise ComfyApiError("Unexpected response payload from /system_stats")
    return data


def ping(prefs: ComfyAddonPreferences, timeout: float = DEFAULT_TIMEOUT) -> bool:
    try:
        system_stats(prefs, timeout=timeout)
    except (requests.RequestException, ComfyApiError):
        return False
    return True


def send_prompt(prefs: ComfyAddonPreferences, workflow_json: Dict[str, Any], timeout: float = DEFAULT_TIMEOUT) -> Any:
    url = f"{prefs.base_url()}/prompt"
    return _request_json("POST", url, timeout=timeout, json_payload=workflow_json)
