# Blender × ComfyUI Bridge (Phase A)

This repository contains a work-in-progress Blender add-on that helps artists interact with a local [ComfyUI](https://github.com/comfyanonymous/ComfyUI) instance without leaving Blender. The current focus is the Phase A milestone – starting/stopping ComfyUI, streaming its logs into Blender, and driving an external webview pointed at the ComfyUI frontend.

## Features

- Configure ComfyUI install & Python paths via add-on preferences.
- Start/stop a local ComfyUI server directly from an N-panel in the 3D Viewport.
- Stream ComfyUI stdout/stderr logs into Blender with a multi-line text box.
- Ping the ComfyUI REST API to verify connectivity.
- Launch/focus/close a pywebview-powered external window pointed at `http://<host>:<port>`.
- Extensible module layout that prepares for the Phase B embedded Chromium workflow.

## Requirements

- Blender 4.0 or newer (Python 3.11 runtime).
- A working ComfyUI checkout containing `main.py`.
- Optional: [pywebview](https://pywebview.flowrl.com/) installed into Blender's Python environment for the Phase A webview controls.
- Optional: `requests` Python package (Blender bundles it by default, but custom builds may not).

## Installing the add-on

1. Clone/download this repository.
2. Zip the `blender-comfyui/addon` folder (e.g. `zip -r blender-comfyui.zip blender-comfyui/addon`).
3. In Blender, open **Edit → Preferences… → Add-ons → Install…**, pick the generated zip, and enable the add-on.
4. Open the add-on preferences to configure:
   - **ComfyUI Folder**: the directory containing ComfyUI's `main.py`.
   - **Python Executable** (optional): override interpreter path.
   - **Host/Port**: defaults to `127.0.0.1:8188`.
   - **Log History Lines**: number of lines preserved in the log buffer.
   - **Always on Top**: whether the external webview stays above other windows.

After configuring, open the **View3D → Sidebar → ComfyUI** panel. Use **Start ComfyUI** to launch the server and **Open ComfyUI Webview** to spawn the external window.

## Troubleshooting

- **pywebview missing**: Install it into Blender's bundled Python with `"<blender.exe>\python\bin\python.exe" -m pip install pywebview`.
- **Python executable not found**: Set an explicit interpreter path in preferences.
- **Logs not updating**: Ensure the add-on is enabled and ComfyUI is running; the log buffer refreshes twice a second.

## Repository layout

```
blender-comfyui/
  addon/               # Blender add-on modules
  docs/                # Additional documentation & packaging notes
  tests/manual-checklist.md
```

Phase B (embedded Chromium via CEF) scaffolding lives in `addon/cef_embed.py`, `addon/draw.py`, and `addon/events.py` but is not yet implemented.

## License

This project uses permissive dependencies only. See [`docs/license-notices.md`](docs/license-notices.md) for third-party acknowledgements. All custom code in this repository is MIT licensed.
