"""Blender × ComfyUI add-on bootstrap package."""
from __future__ import annotations

import importlib
from types import ModuleType
from typing import Iterable, List

import bpy

bl_info = {
    "name": "Blender × ComfyUI Bridge",
    "author": "OpenAI Assistant",
    "version": (0, 1, 0),
    "blender": (4, 0, 0),
    "location": "View3D > Sidebar > ComfyUI",
    "description": "Control a local ComfyUI server and surface its UI/logs inside Blender.",
    "warning": "Proof-of-concept implementation of Phase A",
    "doc_url": "https://github.com/",
    "category": "System",
}


_MODULES: List[ModuleType] = []


def _load_modules() -> Iterable[ModuleType]:
    module_names = (
        "prefs",
        "manager",
        "api_bridge",
        "webview_external",
        "ui_panel",
        "cef_embed",
        "draw",
        "events",
    )

    loaded: List[ModuleType] = []
    package = __name__
    for name in module_names:
        full_name = f"{package}.{name}"
        module = importlib.import_module(full_name)
        if module not in loaded:
            loaded.append(module)
    return loaded


def register() -> None:
    global _MODULES

    modules = list(_load_modules())
    for module in modules:
        if hasattr(module, "register"):
            module.register()
    _MODULES = modules


def unregister() -> None:
    global _MODULES

    for module in reversed(_MODULES):
        if hasattr(module, "unregister"):
            try:
                module.unregister()
            except Exception:  # pragma: no cover - defensive
                import traceback

                traceback.print_exc()
    _MODULES.clear()


if __name__ == "__main__":  # pragma: no cover - manual debugging helper
    register()
