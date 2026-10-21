# Make this application yours

This package contains the active instructions for Demo2. No code edits or server
redeployment are needed to apply the supported changes.

1. Download the instruction package from Customize.
2. Attach its four Markdown files to ChatGPT and describe your change.
3. Ask ChatGPT for the complete revised files. Review the text yourself.
4. Upload the changed Markdown files under Customize (not Case documents).
5. Review the exact before/after changes and click Apply reviewed changes.
6. Run a fresh AI review. Earlier assessments retain their original instructions.

## What each file controls

- workflow.md: how evidence is evaluated, how gaps are handled, and how follow-up
  is drafted. Natural-language business rules belong here.
- checklist.md: the fields to evaluate, who owns each field, and when each is
  required or optional. Keep the four-column Markdown table. New IDs use lowercase
  letters, numbers, and hyphens; owners are client, escrow, or internal.
- SKILL.md: the overall task instructions. Keep its front matter name unchanged.
  Its reference paths are mapped to the other files when the application runs.
- ui.md: the visible brand, headline, intro, review button, colors, and whether
  assistant, history, and source sections are shown. Keep the labels unchanged.
  Use yes/no switches and six-digit hex colors. Text outside the supported fields
  is guidance and does not create new UI behavior. Arbitrary layout/code edits
  require developer work.

## Suggested ChatGPT request

I'm customizing an application through Markdown configuration files. Read the
attached SKILL.md, workflow.md, checklist.md, and ui.md. Make only this change:
[DESCRIBE THE CHANGE]. Explain what you changed, then return each changed file in
full as a downloadable Markdown file, preserving its filename. Preserve valid
front matter, the checklist table columns and unique IDs, and ui.md field labels.
Do not include executable code or ask for API keys. Do not weaken evidence,
privacy, or draft-only boundaries. Do not change files unrelated to my request.

## Try a visible business-rule change

“Make the client's phone number optional at intake. Do not request a missing
owner or primary-contact phone number in the follow-up. Change the main heading
to 'A simpler intake for your team' and hide the assistant panel.”

For phone changes, edit both owner-phone and contact-phone requirements in
checklist.md and align workflow.md. The AI still evaluates the evidence; the
application validates the structure against the active checklist.

## Versions and boundaries

Changes apply only to this signed-in browser session. Other visitors and Demo1
are unaffected. Review and apply a proposal before it becomes active. Restore an
older version from Customize to undo a change. Restore then rerun the review to
make results consistent with the restored rules. New cases preserve active
instructions. Signing out ends the session; download the package to keep it.

Uploaded instructions cannot change API keys, access controls, Python code,
network access, output validation, or email sending. They are configurable
business policies, not a security boundary or a guarantee of correct AI judgment.
