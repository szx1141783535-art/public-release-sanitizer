# Public Release Sanitizer Checklist

Use this checklist before publishing, uploading, sharing, emailing, packaging, or otherwise releasing files outside a private workspace.

## Public Boundary

Before release, confirm:

- The artifact is the intended public version, not a renamed internal draft.
- The visible text is written for its real public audience, not for the project owner, an assistant, or an internal reviewer.
- File names, archive names, table captions, slide notes, document properties, comments, and hidden workbook/speaker-note text are also public-clean.
- No local paths, temp paths, screenshots, clipboard names, home directories, machine-specific locations, or private workspace folders remain.
- No secrets or secret-like material remains: API keys, tokens, passwords, bearer headers, credentials, cookies, private keys, or `.env` values.
- No personal data remains unless release is intentional and permitted: emails, phone numbers, addresses, IDs, account names, patient/student/customer records, or identifiable private details.
- No internal conversation remains: "send to user", "waiting for review", "model said", "assistant task", "chat notes", "round review", "decision packet", or similar routing/process language.
- No tool/runtime transcript remains: "Thinking", "Tool actions", "Ran ...", "Browser Console", captured page snapshots, retry errors, terminal logs, or agent status text.
- No chat-facing tone remains: "as requested", "you asked", "I fixed", "下面是", "按你的要求", "我已经", or other prose addressed to the requester rather than to the public reader.
- No draft-only labels remain: TODO, TBD, FIXME, XXX, placeholder text, review comments, internal-only warnings, or "do not publish" notes.
- No internal identifiers remain unless explained as public identifiers: private row IDs, target IDs, paper IDs, provisional screening IDs, ticket IDs, or local database IDs.

## Rewrite Guidance

Rewrite internal text into public-facing prose:

- "You should upload this" -> "This file is included for public review."
- "A model reviewed this" -> remove it, or use a required public disclosure if the venue requires one.
- "User approved this on 2026-06-15" -> "The release version was finalized on 2026-06-15."
- "DRAFT_INTERNAL / review only / final_review" -> remove from the public artifact.
- "<local-user-home>/Desktop/file.docx" -> replace with a public filename or remove the path.

## If the Scanner Blocks

Stop the release. Choose one:

- Rewrite or remove the flagged content and rescan.
- Replace the file with a clean exported artifact and rescan.
- Add a narrow allowlist entry only when the flagged text is legitimate public content and the reason is documented.
- If a real secret or sensitive identifier was found, treat it as exposed and rotate or remediate before release.
