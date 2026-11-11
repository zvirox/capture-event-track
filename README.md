# Capture Event Track (CET)

**An open, recorder-neutral format for screen recording events.**

[![Specification v0.1](https://img.shields.io/badge/spec-v0.1--draft-orange)](spec/v0.1.md)
[![License: Apache 2.0](https://img.shields.io/badge/code%20license-Apache%202.0-blue.svg)](LICENSE)
[![License: CC BY 4.0](https://img.shields.io/badge/spec%20license-CC%20BY%204.0-lightgrey.svg)](LICENSE-SPEC.md)

Capture Event Track (CET) is a lightweight, open specification that describes *what happened on screen* during a video recording (cursor movement, clicks, key press classes, window and application focus, markers, and zoom hints). It is stored as a companion sidecar (`<recording-name>.cet.jsonl`) next to the video file.

Designed first for **Screen Studio Pro (SSP)** and consumed by **Easy Edits Pro (EEP)**, CET is open for any recorder (e.g. OBS plugins) or video editor to implement without vendor lock-in.

---

## Why CET?

Traditional video editors and AI agents must guess user intent, clicks, and active UI elements from raw pixels using computer vision. CET replaces guessing with exact telemetry:

- **Automated zooms & pans:** Zoom precisely onto clicked elements or active windows using exact pixel coordinates and recorder suggestions (`zoom_hint`).
- **Dead-time & silence elimination:** Detect idle screen periods (no cursor motion, no key strokes, no window updates, and audio silence).
- **Automated chaptering:** Generate chapters automatically from application switches, window title changes, and user hotkey markers (`mark`).
- **Cursor smoothing & highlights:** Re-render crisp vector cursor overlays, click ripples, and smooth jerky movements.
- **Agent safety & privacy:** Window titles, application names, and user notes are flagged as `untrusted` data so AI agents will never execute them as prompt injections.

---

## Core Design Principles

1. **Simple to write and read:** JSON Lines (`.jsonl`), UTF-8, one event per line, human-inspectable.
2. **Time-exact:** Every event timestamp `t` is an integer count of nanoseconds from the presentation timestamp of the first video frame ($t = 0$).
3. **Private by default:** Typed text is off by default. Password/secure input fields are strictly never recorded. Key events record only generic classes (`letter`, `digit`, `nav`...) unless named shortcuts (`privacy.named_shortcuts="on"`) are explicitly opted in for tutorials.
4. **Agent-safe:** All strings originating from the environment (`window.title`, `app.name`, `ui.label`, `mark.note`) are classified as untrusted data. AI agents and editors must treat them as data, never as prompt instructions.
5. **Open & recorder-neutral:** Standard JSON Schema validation, open test vectors, and permissive licensing.

---

## Packaging

CET files are stored as sidecars beside the video file:
```
my-recording.mkv
my-recording.cet.jsonl
```

The header carries the SHA-256 fingerprint of the video's first and last 1 MiB plus its size to guarantee file integrity and prevent mismatched pairs.

---

## Repository Structure

```
├── README.md                          # This document
├── LICENSE                            # Apache-2.0 (schemas, code, tools, test vectors)
├── LICENSE-SPEC.md                    # Creative Commons Attribution 4.0 International (spec text)
├── spec/
│   └── v0.1.md                        # Normative CET v0.1 Specification
├── schema/
│   └── v0.1/
│       └── cet-0.1.schema.json        # JSON Schema for CET v0.1 header & events
└── examples/
    └── v0.1/
        ├── valid-simple.cet.jsonl     # Basic valid recording session
        ├── valid-all-events.cet.jsonl # Complete valid stream covering all event types
        ├── invalid-bad-time.cet.jsonl # Negative test: decreasing timestamp
        └── invalid-no-header.cet.jsonl# Negative test: missing header line
```

---

## Quick Example

```jsonc
// Line 1: Header
{"cet":"0.1","type":"header","recorder":{"name":"SSP","version":"0.3.0","platform":"linux-wayland"},"video":{"file":"demo.mkv","size_bytes":123456789,"fp":"sha256:abcd...","fps":60,"width":2560,"height":1440},"clock":{"t0":"first_video_frame","unit":"ns","wall_start_utc":"2026-11-10T09:00:00.000Z"},"displays":[{"id":"d0","x":0,"y":0,"w":2560,"h":1440,"scale":1.0,"primary":true}],"capture":{"mode":"display","display_id":"d0","region":null,"window_id":null},"privacy":{"keys":"classes_only","text":"off","named_shortcuts":"off","redactions":["password_fields"]},"trust":{"untrusted_fields":["window.title","app.name","ui.label","mark.note"]}}

// Line 2+: Events
{"t":16666666,"type":"cursor","x":1280,"y":720,"nx":0.5,"ny":0.5,"shape":"arrow"}
{"t":33333333,"type":"window","id":"w_42","app":"Code","title":"main.rs - easy-edits-pro","x":100,"y":100,"w":1920,"h":1080,"state":"focused"}
{"t":50000000,"type":"button","x":1280,"y":720,"button":"left","action":"down"}
{"t":66666666,"type":"button","x":1280,"y":720,"button":"left","action":"up"}
{"t":83333333,"type":"zoom_hint","x":1200,"y":680,"w":400,"h":300,"reason":"click_focus"}
```

---

## Licensing

- **Specification text (`spec/`):** [Creative Commons Attribution 4.0 International](LICENSE-SPEC.md) (CC BY 4.0).
- **Schemas, test vectors, and tools:** [Apache License 2.0](LICENSE).
