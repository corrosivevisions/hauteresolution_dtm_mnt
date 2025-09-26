# Build Matrix & Dependency Notes

The add-on targets Blender 4.x which bundles Python 3.11 on all desktop platforms. The following table captures the expected compatibility targets for both the Phase A (pywebview) and Phase B (CEF) milestones.

| Platform | Blender Version | Python ABI | Phase A Dependencies | Phase B Dependencies |
|----------|-----------------|------------|-----------------------|----------------------|
| Windows 11 (x64) | 4.0 – 4.2 | CPython 3.11 | `pywebview>=4.4`, `requests` | `cefpython3` wheel built for Python 3.11, `numpy` (transitive) |
| Linux (Ubuntu 22.04+) | 4.0 – 4.2 | CPython 3.11 | `pywebview>=4.4` (GTK backend) | `cefpython3` manylinux wheel (pending) |
| macOS 14 (Apple Silicon) | 4.0 – 4.2 | CPython 3.11 | `pywebview>=4.4` (Cocoa backend) | `cefpython3` universal2 build (pending upstream) |

Notes:

- Blender for Windows ships with an embedded Python interpreter located at `blender.exe\..\python\bin\python.exe`. The add-on can bootstrap packages via `pip` using this interpreter.
- `pywebview` offers multiple GUI backends. For Windows we recommend the default MSHTML/Edge backend. Linux requires GTK packages installed system-wide.
- `cefpython3` packages are large. The Phase B work will either vendor pre-built wheels (recommended for Windows) or download them on first run.
- Keep an eye on GPU driver compatibility: CEF's accelerated compositing requires up-to-date drivers on NVIDIA/AMD cards.
