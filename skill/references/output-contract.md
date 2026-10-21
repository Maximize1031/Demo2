# Markdown output and UI contract

Write `assessment.md` with this exact table shape (one row per checklist ID, no omissions or duplicates):

| ID | Item | State | Owner | Value | Evidence |
| --- | --- | --- | --- | --- | --- |
| closing | Estimated closing date | conflict | escrow | November 6 vs November 9, 2026 | 02-sale-agreement.md §Closing: Nov 6; 03-email-thread.md §Message 2: Nov 9 |

Use Markdown headings before the table for case name and mode; add `## Change log` after it. Escape any literal pipe as `&#124;` and use one physical line per row. For missing/optional items, evidence names the reviewed set. For not-applicable rows, state the condition and source. Do not save raw tax identifiers.

Write `client-email.md` and `escrow-email.md` as ordinary plain-text Markdown. Start with `To:`, optional `Cc:`, then `Subject:` and the body. Addresses must come from evidence; no guessed addresses. When no follow-up is needed, write that as the full file. Preserve a draft-only label in the UI, not in the client-facing body.

Run:

```text
python3 scripts/render_view.py --run-dir <absolute-run-directory> --output <absolute-intake-view.html>
```

The helper reads only the three Markdown outputs and the checklist. It checks complete IDs, state/owner values, and missing evidence on found/conflict rows, computes displayed counts, escapes inserted data, and fills the HTML asset. It does not validate the truth of the model's assessment or extract data. Review evidence and drafts before rendering.

The website renders validated data using its own interface. Do not use ChatGPT,
Visualize, browser tools, or inline visualization references. The bundled HTML
renderer is a Python validation step only.

Required assessment metadata before the table:

```text
Case: <case name supplied by the application>
Case ID: <case ID supplied by the application>
Property: <property established by the evidence, or Not yet established>
Mode: Synthetic post-ingestion workflow demonstration
Revision: <current revision label>
Source records: <actual number of records supplied>
```

Return the complete documents in JSON fields `assessment`, `client_email`, and
`escrow_email`. The application saves versioned results and renders the interface.
