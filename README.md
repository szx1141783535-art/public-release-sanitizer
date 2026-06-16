# Public Release Sanitizer

Public Release Sanitizer is a conservative pre-release scanner for files that are about to leave a private workspace. It checks for content that should usually be removed before publishing, sharing, attaching, or packaging files.

It is designed to catch:

- secret-like strings and credentials
- private local paths and private hosts
- internal process notes and review labels
- assistant, model, and automation traces
- placeholders and draft labels
- private row IDs or local identifiers
- possible personal contact data

## Repository Layout

```text
.
├── SKILL.md
├── README.md
├── scripts/
│   └── scan_public_release.py
├── references/
│   └── checklist.md
├── agents/
│   └── openai.yaml
└── tests/
    └── test_scan_public_release.py
```

## Usage

From this directory:

```powershell
python scripts/scan_public_release.py scan <files-or-dirs> --report public_release_scan.md --json public_release_scan.json
```

Add project-specific JSON rules when needed:

```powershell
python scripts/scan_public_release.py scan <files-or-dirs> --rules custom_rules.json --report public_release_scan.md --json public_release_scan.json
```

Custom rules must be a JSON list:

```json
[
  {
    "rule": "PROJECT_PRIVATE_TERM",
    "severity": "medium",
    "pattern": "PROJECT_INTERNAL_NAME",
    "suggestion": "Remove or rename the project-private term before release."
  }
]
```

## Exit Codes

- `0`: no blocking findings
- `1`: at least one active high or medium finding
- `2`: missing, unreadable, unsupported, or unscannable explicit input
- `3`: script error

## Requirements

- Python 3.10+
- No required third-party dependencies for text, code, configuration, or Office XML files
- Optional PDF extraction support through `pypdf`, `PyPDF2`, or `pdfplumber`

PDF files fail closed when text cannot be extracted.

## Tests

Run the standard-library test suite from this directory:

```powershell
python -m unittest discover -s tests
```

## Notes for Maintainers

This repository intentionally contains scanner rules and documentation examples for terms the scanner is designed to detect. A self-scan can therefore report expected findings in the scanner source or checklist. Review those findings as intentional public documentation, and still treat any unrelated finding as a release blocker.
