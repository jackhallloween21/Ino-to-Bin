#!/usr/bin/env python3
"""
ino2bin — compile Arduino .ino sketches into .bin firmware for ESP8266/ESP32.

Wraps the official Arduino CLI (https://arduino.github.io/arduino-cli/latest/)
so compiling a sketch is a single reproducible command, in CI or locally.

Usage:
    python ino2bin.py --sketch sketches/my_project --board esp8266:esp8266:nodemcuv2
    python ino2bin.py --sketch sketches/my_project --board esp32:esp32:esp32 --output-dir build/esp32

Common board FQBNs:
    ESP8266 NodeMCU 1.0 : esp8266:esp8266:nodemcuv2
    ESP8266 Generic      : esp8266:esp8266:generic
    ESP32 Dev Module      : esp32:esp32:esp32
"""

from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def find_arduino_cli(explicit_path: str | None) -> str:
    candidate = explicit_path or "arduino-cli"
    resolved = shutil.which(candidate)
    if not resolved:
        sys.exit(
            f"[ino2bin] ERROR: could not find '{candidate}' on PATH.\n"
            f"          Install it from https://arduino.github.io/arduino-cli/latest/installation/ "
            f"or pass --arduino-cli-path /full/path/to/arduino-cli"
        )
    return resolved


def resolve_sketch_dir(sketch_arg: str) -> Path:
    """
    Arduino CLI requires the sketch folder name to match its .ino file name
    (e.g. my_project/my_project.ino). Accept either the folder or the .ino
    file itself and validate the structure, with a clear error if it's wrong.
    """
    path = Path(sketch_arg).resolve()

    if path.is_file():
        if path.suffix != ".ino":
            sys.exit(f"[ino2bin] ERROR: '{path}' is not a .ino file.")
        sketch_dir = path.parent
        ino_file = path
    elif path.is_dir():
        sketch_dir = path
        ino_candidates = list(sketch_dir.glob("*.ino"))
        if not ino_candidates:
            sys.exit(f"[ino2bin] ERROR: no .ino file found inside '{sketch_dir}'.")
        if len(ino_candidates) > 1:
            sys.exit(
                f"[ino2bin] ERROR: multiple .ino files found in '{sketch_dir}': "
                f"{[f.name for f in ino_candidates]}. A sketch folder must contain exactly one."
            )
        ino_file = ino_candidates[0]
    else:
        sys.exit(f"[ino2bin] ERROR: '{sketch_arg}' does not exist.")

    if ino_file.stem != sketch_dir.name:
        sys.exit(
            f"[ino2bin] ERROR: folder/file name mismatch.\n"
            f"          Arduino CLI requires the sketch folder and its .ino file to share the "
            f"same name.\n"
            f"          Found folder '{sketch_dir.name}' containing '{ino_file.name}'.\n"
            f"          Fix: rename the folder to '{ino_file.stem}', or rename "
            f"'{ino_file.name}' to '{sketch_dir.name}.ino'."
        )

    return sketch_dir


def compile_sketch(arduino_cli: str, sketch_dir: Path, board_fqbn: str, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    cmd = [
        arduino_cli, "compile",
        "--fqbn", board_fqbn,
        "--output-dir", str(output_dir),
        str(sketch_dir),
    ]
    print(f"[ino2bin] Compiling '{sketch_dir.name}' for {board_fqbn} ...")
    print(f"[ino2bin] $ {' '.join(cmd)}")

    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print(result.stdout)
        print(result.stderr, file=sys.stderr)
        sys.exit(
            f"[ino2bin] ERROR: compilation failed for '{sketch_dir.name}' ({board_fqbn}).\n"
            f"          See the arduino-cli output above for the specific error "
            f"(missing library, board core not installed, syntax error, etc.)."
        )

    print(result.stdout)

    bin_files = sorted(output_dir.glob("*.bin"))
    if not bin_files:
        sys.exit(
            f"[ino2bin] ERROR: compile reported success but no .bin file was found in "
            f"'{output_dir}'. This can happen with some board cores that only produce a .elf; "
            f"check arduino-cli's output above."
        )

    for bf in bin_files:
        print(f"[ino2bin] Built: {bf}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Compile an Arduino .ino sketch into a .bin firmware file for ESP8266/ESP32."
    )
    parser.add_argument(
        "--sketch", required=True,
        help="Path to the sketch folder or .ino file (folder and .ino name must match)."
    )
    parser.add_argument(
        "--board", required=True,
        help="Target board FQBN, e.g. esp8266:esp8266:nodemcuv2 or esp32:esp32:esp32."
    )
    parser.add_argument(
        "--output-dir", default="build",
        help="Directory to write the compiled .bin into (default: ./build)."
    )
    parser.add_argument(
        "--arduino-cli-path", default=None,
        help="Path to the arduino-cli executable, if not on PATH."
    )
    args = parser.parse_args()

    arduino_cli = find_arduino_cli(args.arduino_cli_path)
    sketch_dir = resolve_sketch_dir(args.sketch)
    output_dir = Path(args.output_dir).resolve()

    compile_sketch(arduino_cli, sketch_dir, args.board, output_dir)


if __name__ == "__main__":
    main()
