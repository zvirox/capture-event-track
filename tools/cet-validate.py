#!/usr/bin/env python3
"""
Capture Event Track (CET) Conformance Validator v0.1
Checks CET JSON Lines files against structure, monotonic time, and size constraints.
"""
import sys
import json
import argparse
from pathlib import Path

MAX_LINE_LENGTH = 65536
MAX_STRING_LENGTH = 1024
VALID_EVENT_TYPES = {
    "cursor", "button", "scroll", "key", "text", "window",
    "ui", "mark", "zoom_hint", "audio", "pause", "annotation"
}

def validate_cet_file(file_path: Path) -> tuple[bool, str]:
    if not file_path.is_file():
        return False, f"File not found: {file_path}"

    with open(file_path, "r", encoding="utf-8") as f:
        line_num = 0
        last_t = -1
        has_header = False

        for raw_line in f:
            line_num += 1
            line = raw_line.rstrip("\r\n")

            if len(raw_line) > MAX_LINE_LENGTH:
                return False, f"Line {line_num}: Exceeds maximum line limit of {MAX_LINE_LENGTH} bytes."

            if not line.strip():
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                return False, f"Line {line_num}: Malformed JSON - {e}"

            if not isinstance(record, dict):
                return False, f"Line {line_num}: Record must be a JSON object."

            if line_num == 1:
                # Line 1 must be header
                if record.get("type") != "header" or record.get("cet") != "0.1":
                    return False, f"Line 1: Must be a CET v0.1 header object (got type={record.get('type')}, cet={record.get('cet')})."
                for req in ["recorder", "video", "clock", "displays", "capture", "privacy", "trust"]:
                    if req not in record:
                        return False, f"Line 1: Header missing required key '{req}'."
                has_header = True
                continue

            if not has_header:
                return False, f"Line {line_num}: Stream has no valid header on Line 1."

            # Line 2+ are events
            t = record.get("t")
            if t is None or not isinstance(t, int) or t < 0:
                return False, f"Line {line_num}: Event missing valid non-negative integer timestamp 't'."

            if t < last_t:
                return False, f"Line {line_num}: Timestamp non-monotonic ({t} < previous {last_t})."
            last_t = t

            etype = record.get("type")
            if not etype or not isinstance(etype, str):
                return False, f"Line {line_num}: Event missing 'type' string."

            # Check known event types or vendor extension
            if etype not in VALID_EVENT_TYPES and not etype.startswith("x-"):
                # Unknown types are ignored per spec §2.5, but type must be valid identifier
                pass

            # Check string limits
            for k, v in record.items():
                if isinstance(v, str) and len(v.encode("utf-8")) > MAX_STRING_LENGTH:
                    return False, f"Line {line_num}: Field '{k}' exceeds {MAX_STRING_LENGTH} bytes limit."

    if line_num == 0:
        return False, "File is completely empty."

    if not has_header:
        return False, "No header record found."

    return True, f"Valid CET v0.1 file ({line_num} records checked, max t={last_t} ns)."

def main():
    parser = argparse.ArgumentParser(description="Validate a CET v0.1 JSON Lines file.")
    parser.add_argument("file", type=Path, help="Path to .cet.jsonl file")
    args = parser.parse_args()

    ok, message = validate_cet_file(args.file)
    print(f"[{'PASS' if ok else 'FAIL'}] {message}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
