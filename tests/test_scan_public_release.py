from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "scan_public_release.py"


class ScanPublicReleaseTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )

    def write_text(self, root: Path, relative: str, text: str) -> Path:
        path = root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def scan_path(self, path: Path, *extra: str) -> tuple[int, dict]:
        json_path = path.parent / "scan.json"
        result = self.run_cli("scan", str(path), *extra, "--json", str(json_path))
        payload = json.loads(json_path.read_text(encoding="utf-8")) if json_path.exists() else {}
        return result.returncode, payload

    def test_help(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("scan", result.stdout)

    def test_clean_markdown_passes(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = self.write_text(Path(temp), "clean.md", "Public release notes.")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 0)
        self.assertEqual(payload["blocking_findings"], 0)

    def test_secret_like_material_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            key_name = "OPENAI" + "_API" + "_KEY"
            key_value = "sk" + "-" + ("1" * 20)
            path = self.write_text(Path(temp), "config.env", f"{key_name}={key_value}")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 1)
        self.assertGreaterEqual(payload["blocking_findings"], 1)

    def test_internal_filename_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            filename = "DRAFT" + "_INTERNAL_notes.md"
            path = self.write_text(Path(temp), filename, "Public content.")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 1)
        rules = {finding["rule"] for finding in payload["findings"]}
        self.assertIn("DRAFT_OR_REVIEW_NOTE", rules)

    def test_tool_trace_and_chat_tone_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            tool_trace = "Think" + "ing\nTool " + "actions\nCaptured page " + "snapshot"
            chat_tone = "\u6309\u4f60\u7684\u8981\u6c42\uff0c\u6211\u5df2\u7ecf\u66f4\u65b0\u3002"
            path = self.write_text(Path(temp), "notes.txt", f"{tool_trace}\n{chat_tone}")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 1)
        rules = {finding["rule"] for finding in payload["findings"]}
        self.assertIn("TOOL_OR_RUNTIME_TRACE", rules)
        self.assertIn("NON_PUBLIC_TONE_OR_DIRECTIVE", rules)

    def test_low_risk_contact_warning_does_not_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            email = "release" + "@" + "example.org"
            path = self.write_text(Path(temp), "contact.md", f"Contact: {email}")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 0)
        self.assertEqual(payload["blocking_findings"], 0)
        self.assertEqual(payload["findings"][0]["severity"], "low")

    def test_custom_rules_block(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            rules = root / "rules.json"
            rules.write_text(
                json.dumps(
                    [
                        {
                            "rule": "PROJECT_PRIVATE_TERM",
                            "severity": "medium",
                            "pattern": "PROJECT_PUBLIC_BLOCK",
                            "suggestion": "Remove the project-private term.",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            path = self.write_text(root, "custom.md", "PROJECT_PUBLIC_BLOCK")
            code, payload = self.scan_path(path, "--rules", str(rules))
        self.assertEqual(code, 1)
        self.assertEqual(payload["findings"][0]["rule"], "PROJECT_PRIVATE_TERM")

    def test_allowlist_releases_matching_finding(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            key_name = "OPENAI" + "_API" + "_KEY"
            key_value = "sk" + "-" + ("1" * 20)
            path = self.write_text(root, "config.env", f"{key_name}={key_value}")
            first_code, first_payload = self.scan_path(path)
            self.assertEqual(first_code, 1)
            finding = first_payload["findings"][0]
            allowlist = root / "allowlist.json"
            allowlist.write_text(
                json.dumps(
                    [
                        {
                            "rule": finding["rule"],
                            "file": "config.env",
                            "text": finding["snippet"],
                            "reason": "Unit test fixture uses generated sample material.",
                        }
                    ]
                ),
                encoding="utf-8",
            )
            code, payload = self.scan_path(path, "--allowlist", str(allowlist))
        self.assertEqual(code, 0)
        self.assertEqual(payload["blocking_findings"], 0)
        self.assertTrue(payload["findings"][0]["allowed"])

    def test_unsupported_explicit_file_returns_2(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "asset.bin"
            path.write_bytes(b"\x00\x01")
            code, payload = self.scan_path(path)
        self.assertEqual(code, 2)
        self.assertEqual(payload["extraction_issues"][0]["issue"], "UNSUPPORTED_FILE")


if __name__ == "__main__":
    unittest.main()
