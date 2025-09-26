"""UI elements and operators for the Blender × ComfyUI bridge."""
from __future__ import annotations

import bpy
from bpy.types import Operator, Panel

from . import api_bridge
from .manager import get_manager
from .prefs import get_preferences
from .webview_external import WindowBounds, get_controller


class BLENDCOMFY_OT_start_server(Operator):
    bl_idname = "blendcomfy.start_server"
    bl_label = "Start ComfyUI"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        prefs = get_preferences(context)
        manager = get_manager()
        if manager.is_running:
            self.report({"INFO"}, "ComfyUI server already running")
            return {"CANCELLED"}
        try:
            manager.start(prefs)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        self.report({"INFO"}, "ComfyUI server starting…")
        return {"FINISHED"}


class BLENDCOMFY_OT_stop_server(Operator):
    bl_idname = "blendcomfy.stop_server"
    bl_label = "Stop ComfyUI"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        manager = get_manager()
        if not manager.is_running:
            self.report({"INFO"}, "ComfyUI server is not running")
            return {"CANCELLED"}
        manager.stop()
        self.report({"INFO"}, "ComfyUI server stopped")
        return {"FINISHED"}


class BLENDCOMFY_OT_ping_server(Operator):
    bl_idname = "blendcomfy.ping_server"
    bl_label = "Ping API"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        prefs = get_preferences(context)
        ok = api_bridge.ping(prefs)
        if ok:
            self.report({"INFO"}, "ComfyUI API reachable")
            return {"FINISHED"}
        self.report({"ERROR"}, "Failed to reach ComfyUI API")
        return {"CANCELLED"}


class BLENDCOMFY_OT_open_webview(Operator):
    bl_idname = "blendcomfy.open_webview"
    bl_label = "Open ComfyUI Webview"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        prefs = get_preferences(context)
        controller = get_controller()
        bounds = WindowBounds(*prefs.webview_bounds)
        try:
            controller.open(prefs.base_url(), always_on_top=prefs.always_on_top, bounds=bounds)
        except Exception as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        self.report({"INFO"}, "Opened ComfyUI webview")
        return {"FINISHED"}


class BLENDCOMFY_OT_close_webview(Operator):
    bl_idname = "blendcomfy.close_webview"
    bl_label = "Close ComfyUI Webview"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        controller = get_controller()
        if not controller.is_open():
            self.report({"INFO"}, "ComfyUI webview is not open")
            return {"CANCELLED"}
        controller.close()
        self.report({"INFO"}, "Closed ComfyUI webview")
        return {"FINISHED"}


class BLENDCOMFY_OT_focus_webview(Operator):
    bl_idname = "blendcomfy.focus_webview"
    bl_label = "Focus ComfyUI Webview"
    bl_options = {"REGISTER"}

    def execute(self, context: bpy.types.Context) -> set[str]:
        controller = get_controller()
        if not controller.is_open():
            self.report({"INFO"}, "ComfyUI webview is not open")
            return {"CANCELLED"}
        controller.focus()
        self.report({"INFO"}, "Focused ComfyUI webview")
        return {"FINISHED"}


class BLENDCOMFY_PT_sidebar(Panel):
    bl_idname = "BLENDCOMFY_PT_sidebar"
    bl_label = "ComfyUI"
    bl_category = "ComfyUI"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context: bpy.types.Context) -> None:
        layout = self.layout
        wm = context.window_manager
        prefs = get_preferences(context)
        controller = get_controller()

        row = layout.row()
        row.prop(wm, "blender_comfyui_server_running", text="Server Running", toggle=True)

        row = layout.row()
        row.enabled = not wm.blender_comfyui_server_running
        row.operator(BLENDCOMFY_OT_start_server.bl_idname, icon="PLAY")

        row = layout.row()
        row.enabled = wm.blender_comfyui_server_running
        row.operator(BLENDCOMFY_OT_stop_server.bl_idname, icon="STOP")

        row = layout.row(align=True)
        row.operator(BLENDCOMFY_OT_ping_server.bl_idname, icon="URL")
        row.operator(BLENDCOMFY_OT_open_webview.bl_idname, icon="FILE_FOLDER")
        sub = row.row(align=True)
        sub.enabled = controller.is_open()
        sub.operator(BLENDCOMFY_OT_focus_webview.bl_idname, icon="VIEWZOOM")
        sub.operator(BLENDCOMFY_OT_close_webview.bl_idname, icon="PANEL_CLOSE")

        layout.separator()
        layout.label(text="Logs (latest {} lines):".format(prefs.log_history_lines))
        col = layout.column()
        col.prop(wm, "blender_comfyui_log", text="", slider=False)

        layout.separator()
        validation = prefs.validate()
        icon = "CHECKMARK" if validation.ok else "ERROR"
        layout.label(text=f"Preferences: {validation.message}", icon=icon)


_CLASSES = (
    BLENDCOMFY_OT_start_server,
    BLENDCOMFY_OT_stop_server,
    BLENDCOMFY_OT_ping_server,
    BLENDCOMFY_OT_open_webview,
    BLENDCOMFY_OT_close_webview,
    BLENDCOMFY_OT_focus_webview,
    BLENDCOMFY_PT_sidebar,
)


def register() -> None:
    for cls in _CLASSES:
        bpy.utils.register_class(cls)


def unregister() -> None:
    for cls in reversed(_CLASSES):
        bpy.utils.unregister_class(cls)
