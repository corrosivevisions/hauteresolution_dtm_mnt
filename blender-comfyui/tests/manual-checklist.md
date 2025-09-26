# Manual Testing Checklist

Use this checklist to validate Phase A functionality on each supported platform.

## Environment Prep

- [ ] Install Blender 4.0+ and enable the Blender × ComfyUI add-on.
- [ ] Configure the add-on preferences with a valid ComfyUI folder.
- [ ] Confirm `pywebview` is installed in Blender's Python runtime (`Help → Python Console`, `import webview`).

## ComfyUI Lifecycle

- [ ] Press **Start ComfyUI**. Verify the status toggle flips to *Server Running*.
- [ ] Observe logs updating in real time. Confirm there are no UI freezes while ComfyUI boots.
- [ ] Press **Ping API**. Expect a success toast once ComfyUI is ready.
- [ ] Press **Stop ComfyUI**. Ensure the process terminates quickly and logs stop updating.
- [ ] Repeat the start/stop cycle at least five times.

## External Webview

- [ ] Press **Open ComfyUI Webview**. A window should appear at the configured bounds displaying the ComfyUI UI.
- [ ] Toggle focus using the **Focus Webview** operator.
- [ ] Resize/reposition the window manually, then close it via **Close Webview**.
- [ ] Restart ComfyUI and open the webview again to ensure stability across restarts.

## Error Handling

- [ ] Start the server with an invalid Python executable path and confirm an error is reported.
- [ ] Start the server with an invalid ComfyUI folder and confirm validation prevents launch.
- [ ] Stop Blender while ComfyUI is running and ensure the subprocess terminates.

Document any regressions or platform-specific quirks discovered during testing.
