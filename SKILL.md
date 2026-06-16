---
name: public-release-sanitizer
description: Scan files before public release to decide whether they are safe to publish outside a private workspace. Use for GitHub releases, websites, shared archives, documents, slides, spreadsheets, code packages, attachments, and other outbound files that must be checked for secrets, private paths, personal data, internal process traces, AI/collaboration traces, placeholders, review notes, draft labels, or other public/internal boundary leaks.
---

# Public Release Sanitizer

Use this skill before any file leaves a private workspace. Treat "public" broadly: GitHub, websites, downloadable archives, shared cloud folders, email attachments, manuscripts, supplements, slide decks, code packages, and any file that may be read outside the intended private audience.

## Required Workflow

1. Treat every candidate outbound file as untrusted until scanned.
2. Run the scanner on the exact files or directories that may be released. From this skill directory:

```powershell
python scripts/scan_public_release.py scan <files-or-dirs> --report public_release_scan.md --json public_release_scan.json
```

3. If the scanner returns nonzero, stop release. Remove or rewrite the flagged content, or add a narrow allowlist only when the flagged text is legitimate public content.
4. Do not make an internal work file public by renaming or repackaging it. Create or export a clean public artifact, then scan that artifact.

Optional project-specific rules can be added without modifying the skill:

```powershell
python scripts/scan_public_release.py scan <files-or-dirs> --rules custom_rules.json --report public_release_scan.md --json public_release_scan.json
```

## Blocking Policy

- High or medium findings block release.
- Low findings are warnings, but still review them before release.
- PDF files fail closed when text cannot be extracted.
- Allowlist only when the public material legitimately needs a flagged term. The allowlist entry must include `rule`, `file`, `text`, and `reason`.

## Manual Checklist

Read `references/checklist.md` when preparing public files. Use it to review content that scanners cannot fully understand, including intent, audience, metadata, screenshots, tables, filenames, and context-specific disclosure requirements.

## Script Coverage

The scanner covers common public artifacts:

- Filenames are scanned as release-facing text, so labels such as `DRAFT_INTERNAL`, `review copy`, or private IDs can block even when file contents are clean.
- Text/code/config: `.md`, `.txt`, `.csv`, `.tsv`, `.json`, `.yaml`, `.yml`, `.html`, `.htm`, `.py`, `.R`, `.r`, `.js`, `.jsx`, `.ts`, `.tsx`, `.css`, `.scss`, `.sh`, `.ps1`, `.bat`, `.cmd`, `.sql`, `.toml`, `.ini`, `.cfg`, `.conf`, `.env`, `.xml`, `.qmd`, `.tex`, and common extensionless names such as `.env`, `Dockerfile`, `Makefile`, `package.json`, `pyproject.toml`, `requirements.txt`, lockfiles, and package manifests
- Office: `.docx`, `.xlsx`, `.pptx` via zipped XML text, comments, notes, shared strings, and document properties
- PDF: `pypdf`, `PyPDF2`, or `pdfplumber` when available; otherwise fail closed
- Directory scans skip dependency/cache folders such as `.git`, `node_modules`, `venv`, `.venv`, and `__pycache__`.

## Requirements

- Python 3.10+.
- No required third-party dependencies for text, code, configuration, or Office XML files.
- PDF extraction is optional and uses `pypdf`, `PyPDF2`, or `pdfplumber` when installed. If none are available or a PDF has no extractable text, the scanner fails closed.

Exit codes:

- `0`: no blocking findings
- `1`: active high/medium finding
- `2`: missing, unreadable, unsupported, or unscannable explicit input
- `3`: script error
