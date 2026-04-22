#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "usd-core",
# ]
# ///

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Iterable

from pxr import Tf, Usd


def _format_error_messages(errors: Iterable[object]) -> list[str]:
    messages: list[str] = []
    for err in errors:
        # USD diagnostic objects provide useful string representations.
        text = str(err).strip()
        if text:
            messages.append(text)
    return messages


def open_stage_and_collect_errors(usd_path: Path) -> tuple[Usd.Stage | None, list[str]]:
    if not usd_path.exists():
        return None, [f"File not found: {usd_path}"]

    # Use Tf error marks when available so composition/parser errors can be reported.
    if hasattr(Tf, "Error") and hasattr(Tf.Error, "Mark"):
        mark = Tf.Error.Mark()
        mark.SetMark()
        stage = Usd.Stage.Open(str(usd_path))

        tf_errors = []
        if hasattr(mark, "GetErrors"):
            tf_errors = list(mark.GetErrors())
        if hasattr(mark, "Clear"):
            mark.Clear()

        return stage, _format_error_messages(tf_errors)

    stage = Usd.Stage.Open(str(usd_path))
    return stage, []


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Open a USD file with usd-core and report any open/composition errors."
    )
    parser.add_argument("usd_file", type=Path, help="Path to a USD file (.usd, .usda, .usdc)")
    parser.add_argument(
        "--write-flattened",
        action="store_true",
        help="Write a flattened USDA file next to the input as <original_name>_flattened.usda",
    )
    return parser


def flattened_output_path(usd_path: Path) -> Path:
    return usd_path.with_name(f"{usd_path.stem}_flattened.usda")


def main() -> int:
    args = build_parser().parse_args()
    usd_path = args.usd_file.expanduser().resolve()

    try:
        stage, errors = open_stage_and_collect_errors(usd_path)
    except Exception as exc:  # pragma: no cover - defensive CLI boundary
        print(f"Failed to open USD file: {exc}", file=sys.stderr)
        return 2

    if stage is None:
        if not errors:
            errors = [f"Unable to open stage: {usd_path}"]
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 2

    if args.write_flattened:
        output_path = flattened_output_path(usd_path)
        try:
            flattened_layer = stage.Flatten()
            if not flattened_layer.Export(str(output_path)):
                print(f"ERROR: Failed to write flattened file: {output_path}", file=sys.stderr)
                return 2
            print(f"Wrote flattened layer: {output_path}")
        except Exception as exc:  # pragma: no cover - defensive CLI boundary
            print(f"ERROR: Failed to write flattened file: {exc}", file=sys.stderr)
            return 2

    if errors:
        print(f"Opened stage: {usd_path}")
        print(f"Found {len(errors)} error(s):", file=sys.stderr)
        for msg in errors:
            print(f"ERROR: {msg}", file=sys.stderr)
        return 1

    print(f"Opened stage successfully with no reported errors: {usd_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
