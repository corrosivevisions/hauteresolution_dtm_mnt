# Packaging & Distribution

## Phase A (External Webview)

1. Ensure `pywebview` and `requests` are available in Blender's Python runtime.
2. Zip the `addon/` directory: `cd blender-comfyui && zip -r blender-comfyui-phase-a.zip addon`.
3. Test the archive inside a clean Blender profile by installing the zip through the Add-ons preferences window.
4. Document any additional runtime requirements (GTK, MS Edge WebView2, etc.) per platform.

## Phase B (Embedded Chromium)

1. Download or vendor a matching `cefpython3` wheel for the target platform/ABI.
2. Place the extracted package under `addon/vendor/cefpython3`. Keep the upstream `LICENSE` file intact.
3. Update the add-on to bootstrap/prompt users to download missing binaries.
4. Verify the add-on shuts down CEF cleanly when disabled or when Blender closes.

## Versioning

- Follow semantic versioning `(major, minor, patch)` as exposed through `bl_info['version']`.
- Increment the minor version when adding visible functionality (e.g., Phase B embed).
- Tag releases in source control and attach the packaged zip(s) to GitHub releases.

## Testing Checklist

See [`../tests/manual-checklist.md`](../tests/manual-checklist.md) for manual validation steps across Windows, Linux, and macOS.
