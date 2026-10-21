# Demo2 — Client-configurable intake

Demo2 is a separate copy of Demo1. It adds a client-facing Customize area:
download Markdown instructions, revise them with ChatGPT, review a proposal,
apply it, run a new review, and restore earlier instruction versions.

The original chat demo and the deployed Demo1 are not changed by this project.

## Start locally

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements-dev.txt
cp .env.example .env
.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8002
```

Use the same OpenAI API project configuration as Demo1 in this project's `.env`
or its separate Render service. Never commit secrets. No API key is required to
preview/apply UI changes, review file differences, or run the saved rehearsal.
Live business-rule evaluation requires an API key and model access.

## Demonstrate the customization loop

1. Open Customize and download the instruction package.
2. Attach the four Markdown files to ChatGPT. Copy the suggested prompt and say:
   “Make owner and contact phone numbers optional. Don't ask for absent optional
   phone numbers. Change the main heading to A simpler intake for your team and
   hide the assistant.”
3. Download ChatGPT's revised files, then upload them under Customize.
4. Review the exact diff and proposed appearance. Check the review box and apply.
5. The UI updates immediately. Run a fresh Live AI intake review for the new rules.
6. Open History or download the review to compare results. Each review preserves
   its source files and instruction package. Restore an earlier version to undo.

See [CUSTOMIZE.md](CUSTOMIZE.md) for client instructions. Prepared sample changes
are in `examples/customization/` for a deterministic UI walkthrough. They are
instruction files, not prerecorded AI results.

## How it works

- `workflow.md`: natural-language business policies and follow-up behavior.
- `checklist.md`: dynamic checklist IDs, owners, and requirements. The model and
  Python validator both use the active version; no code edit is needed to change it.
- `SKILL.md`: overall task instructions. The manifest name is fixed.
- `ui.md`: supported text, colors, and section visibility. Parsed deterministically;
  it does not generate arbitrary HTML, CSS, or executable code.
- Fixed application rules retain source citation, output structure, isolation,
  tax-ID receipt-only handling, and draft-only outreach boundaries.

The backend packages the current instructions and selected evidence into an
OpenAI hosted shell container. The model executes the skill and its Python check.
Server-side Python independently validates the returned assessment against the
same active checklist. Only the final structured answer is parsed, excluding
intermediate progress messages.

Instruction versions belong to a signed-in browser session. They survive reloads
and server restarts on the configured disk, but expire with session access after
24 hours. New cases/reset preserve instructions. Sign-out ends the session.
Other visitors and Demo1 are unaffected. Download a package to retain it.

Uploads: Markdown/UTF-8 text evidence only, 100 KB/file and 500 KB/30 records per
case. Customization: four supported Markdown filenames, 50 KB/file, 1–60 checklist
rows, up to 20 instruction versions. Applying or restoring rules marks existing
live results stale until rerun; chat cannot answer against stale results.

AI outcomes still require human review. The validator checks format, IDs, sources,
and selected privacy patterns, not whether every natural-language policy was
interpreted correctly. Custom instructions do not authorize external actions.

## Deploy separately

Repository: https://github.com/Maximize1031/Demo2
Use this repository's `render.yaml` to create a NEW Render service named
`m1031-intake-demo2`. Do not change Demo1's service or repository.
Set `OPENAI_API_KEY` and `DEMO_PASSWORD` (at least 16 characters) in Render.
The blueprint uses a paid Starter service plus a 1 GB persistent disk; review
Render's displayed cost before creating it. Use one worker/process.

## Tests

```sh
.venv/bin/python -m pytest -q
```

Tests cover authentication, uploads, evidence snapshots, isolated sessions, API
contracts, final-message parsing, customization preview/apply/restore, invalid
packages, dynamic checklist validation, stale-result handling, and busy-run locks.
