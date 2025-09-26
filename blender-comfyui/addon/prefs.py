"""Add-on preferences for the Blender × ComfyUI bridge."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import bpy
from bpy.props import BoolProperty, FloatVectorProperty, IntProperty, StringProperty
from bpy.types import AddonPreferences, Context


@dataclass
class ValidationResult:
    ok: bool
    message: str = ""


class ComfyAddonPreferences(AddonPreferences):
    """Preferences exposed under the add-on section in Blender."""

    bl_idname = __package__ or "blender-comfyui.addon"

    comfy_dir: StringProperty(  # type: ignore[assignment]
        name="ComfyUI Folder",
        description="Path to the ComfyUI repository containing main.py",
        subtype="DIR_PATH",
        default="",
    )
    python_exe: StringProperty(  # type: ignore[assignment]
        name="Python Executable",
        description="Optional override for the Python interpreter used to launch ComfyUI",
        subtype="FILE_PATH",
        default="",
    )
    host: StringProperty(  # type: ignore[assignment]
        name="Host",
        default="127.0.0.1",
        description="ComfyUI host to bind and connect to",
    )
    port: IntProperty(  # type: ignore[assignment]
        name="Port",
        default=8188,
        min=1,
        max=65535,
        description="ComfyUI port to bind and connect to",
    )
    log_history_lines: IntProperty(  # type: ignore[assignment]
        name="Log History Lines",
        default=500,
        min=50,
        max=5000,
        description="Maximum number of log lines kept in the in-Blender log buffer.",
    )
    webview_bounds: FloatVectorProperty(  # type: ignore[assignment]
        name="Webview Bounds",
        description="Stored window bounds for the external ComfyUI view (x, y, width, height)",
        subtype="NONE",
        size=4,
        default=(100.0, 100.0, 1280.0, 720.0),
    )
    always_on_top: BoolProperty(  # type: ignore[assignment]
        name="Always on Top",
        description="Keep the external ComfyUI webview floating on top of other windows",
        default=True,
    )

    def draw(self, context: Context) -> None:
        layout = self.layout
        layout.prop(self, "comfy_dir")
        layout.prop(self, "python_exe")
        layout.separator()
        layout.prop(self, "host")
        layout.prop(self, "port")
        layout.separator()
        layout.prop(self, "log_history_lines")
        layout.prop(self, "always_on_top")

        result = self.validate()
        box = layout.box()
        icon = "CHECKMARK" if result.ok else "ERROR"
        box.label(text="Validation: " + (result.message or "OK"), icon=icon)

    def validate(self) -> ValidationResult:
        """Validate the configuration and provide a user-friendly message."""

        comfy_dir_path = Path(self.comfy_dir).expanduser()
        if not comfy_dir_path.exists():
            return ValidationResult(False, "ComfyUI folder does not exist")
        if not comfy_dir_path.is_dir():
            return ValidationResult(False, "ComfyUI path is not a directory")
        main_py = comfy_dir_path / "main.py"
        if not main_py.exists():
            return ValidationResult(False, "ComfyUI main.py was not found in the selected folder")

        if self.python_exe:
            python_path = Path(self.python_exe).expanduser()
            if not python_path.exists():
                return ValidationResult(False, "Python executable override does not exist")
            if not python_path.is_file():
                return ValidationResult(False, "Python executable override is not a file")

        return ValidationResult(True, "Configuration looks good")

    def resolved_python(self) -> Optional[str]:
        """Return the preferred Python executable path or ``None`` if auto-detect should be used."""

        python_override = self.python_exe.strip()
        if python_override:
            return str(Path(python_override).expanduser())
        return None

    def comfy_path(self) -> Path:
        return Path(self.comfy_dir).expanduser()

    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"


def get_preferences(context: Optional[Context] = None) -> ComfyAddonPreferences:
    """Utility to access the add-on preferences from anywhere."""

    context = context or bpy.context
    addon_name = __package__.rsplit(".", 1)[0] if __package__ else "blender-comfyui.addon"
    prefs = context.preferences.addons.get(addon_name)
    if prefs is None:
        raise RuntimeError("Blender × ComfyUI add-on is not registered")
    return prefs.preferences  # type: ignore[return-value]


def register() -> None:
    bpy.utils.register_class(ComfyAddonPreferences)


def unregister() -> None:
    bpy.utils.unregister_class(ComfyAddonPreferences)
