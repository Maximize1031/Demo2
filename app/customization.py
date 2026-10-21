"""Versioned client-editable instructions; application code stays outside the package."""
import difflib
import hashlib
import json
import re
from pathlib import Path

from .workflow import SKILL, SENSITIVE, WorkflowError

EDITABLE = ('SKILL.md', 'workflow.md', 'checklist.md', 'ui.md')
PATHS = {'SKILL.md': 'SKILL.md', 'workflow.md': 'references/workflow.md',
         'checklist.md': 'references/checklist.md'}
UI_FIELDS = {
    'Application name': ('brand', 60), 'Main heading': ('heading', 100),
    'Intro text': ('intro', 240), 'Review button': ('review_button', 50),
    'Accent color': ('accent', 7), 'Background color': ('background', 7),
    'Show assistant': ('show_assistant', 3), 'Show history': ('show_history', 3),
    'Show source documents': ('show_sources', 3),
}
DEFAULT_UI = '''# Website presentation

Edit the values after each colon. Keep the labels unchanged. Use yes/no for visibility,
and a six-digit hex color such as #235347 for colors. These settings change the
website immediately after you review and apply the version. HTML and scripts are
not supported. Larger layout changes require an application update.

Application name: Maximize 1031 · Demo2
Main heading: Your workflow. Your rules.
Intro text: Upload evidence, review the findings, and customize the instructions behind your application.
Review button: Run intake review
Accent color: #235347
Background color: #f6f8f4
Show assistant: yes
Show history: yes
Show source documents: yes
'''


def digest(files):
    return hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()


def defaults():
    files = {name: (SKILL / path).read_text() for name, path in PATHS.items()}
    files['ui.md'] = DEFAULT_UI
    return make_profile(files)


def parse_ui(text):
    result = {}
    for label, (key, limit) in UI_FIELDS.items():
        values = re.findall(r'^' + re.escape(label) + r':\s*([^\n]*)$', text, re.M)
        if len(values) != 1 or not values[0].strip() or len(values[0]) > limit:
            raise WorkflowError(f'ui.md needs exactly one {label}: value, up to {limit} characters.')
        value = values[0].strip()
        if key.startswith('show_'):
            if value.lower() not in ('yes', 'no'):
                raise WorkflowError(f'{label} must be yes or no.')
            result[key] = value.lower() == 'yes'
        elif key in ('accent', 'background'):
            if not re.fullmatch(r'#[0-9a-fA-F]{6}', value):
                raise WorkflowError(f'{label} must be a six-digit hex color, such as #235347.')
            result[key] = value
        else:
            result[key] = value
    return result


def validate_checklist(text):
    rows = []
    for line in text.splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip() for c in line.strip('|').split('|')]
        if cells[0] == 'ID' or re.fullmatch(r'[-: ]+', cells[0]):
            continue
        if len(cells) != 4 or not re.fullmatch(r'[a-z][a-z0-9-]{0,39}', cells[0]):
            raise WorkflowError('checklist.md needs four columns: ID, Item, Owner, Requirement. IDs use lowercase letters, numbers, and hyphens.')
        if cells[2] not in ('client', 'escrow', 'internal') or not cells[1] or not cells[3]:
            raise WorkflowError('Each checklist row needs an item, an owner (client, escrow, internal), and a requirement.')
        rows.append(cells)
    if not 1 <= len(rows) <= 60 or len({r[0] for r in rows}) != len(rows):
        raise WorkflowError('The checklist needs 1–60 unique IDs.')
    return rows


def make_profile(files):
    if set(files) != set(EDITABLE):
        raise WorkflowError('The customization package must contain the four supported Markdown files.')
    for name, text in files.items():
        if not isinstance(text, str) or not text.strip() or len(text.encode()) > 50_000:
            raise WorkflowError(f'{name} must be nonempty UTF-8 text, at most 50 KB.')
        if re.search(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', text) or SENSITIVE.search(text):
            raise WorkflowError('Use readable instructions without tax identifiers.')
    manifest = files['SKILL.md']
    if not manifest.startswith('---\n') or not re.search(r'^name: m1031-intake-web$', manifest, re.M):
        raise WorkflowError('Keep the SKILL.md front matter and name: m1031-intake-web unchanged.')
    if not re.search(r'^description: [^\n]{1,500}$', manifest, re.M):
        raise WorkflowError('SKILL.md needs a one-line description, up to 500 characters.')
    return {'id': digest(files), 'files': files, 'ui': parse_ui(files['ui.md']),
            'checklist_count': len(validate_checklist(files['checklist.md']))}


def propose(active, incoming):
    if not 1 <= len(incoming) <= 4:
        raise WorkflowError('Upload one to four customization files.')
    files = dict(active['files'])
    seen = set()
    for entry in incoming:
        name, text = entry.get('name'), entry.get('text')
        if name not in EDITABLE or name in seen:
            raise WorkflowError('Upload SKILL.md, workflow.md, checklist.md, or ui.md, once each. Keep their filenames unchanged.')
        if not isinstance(text, str):
            raise WorkflowError('Customization files must be UTF-8 text.')
        seen.add(name)
        files[name] = text.removeprefix('\ufeff').replace('\r\n', '\n')
    candidate = make_profile(files)
    if candidate['id'] == active['id']:
        raise WorkflowError('These files match the active version. Edit a file before uploading it.')
    changes = []
    for name in EDITABLE:
        if files[name] != active['files'][name]:
            changes.append({'name': name, 'before': active['files'][name], 'after': files[name],
                            'diff': ''.join(difflib.unified_diff(active['files'][name].splitlines(True), files[name].splitlines(True), fromfile='Active/'+name, tofile='Proposed/'+name))})
    candidate.update(base_id=active['id'], changes=changes)
    return candidate
