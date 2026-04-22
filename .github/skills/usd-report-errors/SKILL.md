---
name: usd-report-errors
description: 'Open a USD file with usd-core and report parser/composition errors. Use when validating .usd/.usda/.usdc files from the CLI.'
---

# USD Error Report CLI

Use this skill when you need to validate whether a USD file opens cleanly and to print any errors reported while opening the stage.

Optionally, it can also write a flattened USDA file.

## Asset

This skill includes the executable script:

- `.github/skills/usd-report-errors/usd_report_errors.py`

## How To Use

Run from the repository root:

```bash
.github/skills/usd-report-errors/usd_report_errors.py "path/to/file.usda"

# Also write path/to/file_flattened.usda
.github/skills/usd-report-errors/usd_report_errors.py --write-flattened "path/to/file.usda"
```

Or run through uv explicitly:

```bash
uv run --script .github/skills/usd-report-errors/usd_report_errors.py "path/to/file.usda"

# Also write path/to/file_flattened.usda
uv run --script .github/skills/usd-report-errors/usd_report_errors.py --write-flattened "path/to/file.usda"
```

## Behavior

- Uses `usd-core` (`pxr.Usd`) to open the stage.
- Collects `pxr.Tf` errors during open when available.
- When `--write-flattened` is provided, writes a flattened file named `<original_name>_flattened.usda` next to the input.
- Prints success when no errors are reported.
- Prints each reported error to stderr.

Exit codes:

- `0`: stage opened with no reported errors
- `1`: stage opened, but one or more errors were reported
- `2`: stage failed to open or script/runtime failure
