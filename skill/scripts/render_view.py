"""Render Markdown assessment and drafts as an in-chat HTML fragment. No extraction."""
import argparse
import html
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STATES = {'found', 'missing', 'conflict', 'review', 'not_applicable', 'optional'}

def table(path):
    rows = []
    for line in path.read_text().splitlines():
        if not line.startswith('|'):
            continue
        cells = [c.strip().replace('&#124;', '|') for c in line.strip('|').split('|')]
        if cells[0] == 'ID' or re.fullmatch(r'[-: ]+', cells[0]):
            continue
        rows.append(cells)
    return rows

def read_assessment(run, checklist_path=None):
    expected = {r[0] for r in table(checklist_path or ROOT / 'references/checklist.md')}
    rows = table(run / 'assessment.md')
    if any(len(r) != 6 for r in rows):
        raise ValueError('Assessment must contain six columns per row')
    ids = [r[0] for r in rows]
    if len(ids) != len(set(ids)) or set(ids) != expected:
        raise ValueError('Checklist IDs are missing, duplicated, or unknown')
    for _, _, state, owner, value, evidence in rows:
        if state not in STATES or owner not in {'client', 'escrow', 'internal'}:
            raise ValueError('Unknown state or owner')
        if state in {'found', 'conflict', 'not_applicable'} and (not evidence or not value):
            raise ValueError('Supported states require value and evidence')
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{2}-\d{7}\b|\b\d{9}\b', value + ' ' + evidence):
            raise ValueError('Possible tax ID; replace with receipt status')
    return rows

def render(run, output, checklist_path=None):
    rows = read_assessment(run, checklist_path)
    raw = (run / 'assessment.md').read_text()
    def meta(key):
        match = re.search(r'^' + re.escape(key) + r': (.+)$', raw, re.M)
        if not match:
            raise ValueError('Missing metadata: ' + key)
        return match[1]
    def esc(value):
        return html.escape(str(value), quote=True)
    labels = {'found':'On file', 'missing':'Missing', 'conflict':'Conflict', 'review':'Needs confirmation', 'not_applicable':'Not applicable', 'optional':'Optional'}
    gaps = [r for r in rows if r[2] in {'missing','conflict','review'}]
    nonblocking = [r for r in rows if r[2] in {'not_applicable','optional'}]
    def row_markup(r):
        return '<div class="intake-row"><div><strong>'+esc(r[1])+'</strong><p class="text-small text-muted">'+esc(labels[r[2]])+' · '+esc(r[3].capitalize())+'</p></div><div><p>'+esc(r[4])+'</p><p class="text-small text-muted">'+esc(r[5])+'</p></div></div>'
    evidence = ''.join('<details><summary>'+esc(r[1])+' · '+esc(labels[r[2]])+'</summary><div class="intake-detail">'+esc(r[4])+'</div><div class="text-small intake-detail">'+esc(r[5])+'</div></details>' for r in rows)
    client=(run/'client-email.md').read_text()
    escrow=(run/'escrow-email.md').read_text()
    for draft in [client,escrow]:
        if re.search(r'\b\d{3}-\d{2}-\d{4}\b|\b\d{2}-\d{7}\b|\b\d{9}\b',draft):
            raise ValueError('Possible tax ID in draft')
    values={
        'ROOT':'intake-'+re.sub('[^a-z0-9-]','',meta('Revision').lower()),
        'CASE':esc(meta('Case')), 'PROPERTY':esc(meta('Property')), 'REVISION':esc(meta('Revision')),
        'SOURCES':esc(meta('Source records')), 'FOUND':str(sum(r[2]=='found' for r in rows)),
        'EXTERNAL':str(sum(r[3]!='internal' for r in gaps)), 'INTERNAL':str(sum(r[3]=='internal' for r in gaps)),
        'CONFLICTS':str(sum(r[2]=='conflict' for r in rows)), 'TOTAL':str(len(rows)), 'NONBLOCKING':str(len(nonblocking)),
        'GAPS':''.join(row_markup(r) for r in gaps) or '<p>No unresolved checklist items. Review before handoff.</p>',
        'OPTIONAL':''.join(row_markup(r) for r in nonblocking),'EVIDENCE':evidence,
        'CLIENT_EMAIL':esc(client),'ESCROW_EMAIL':esc(escrow)
    }
    template=(ROOT/'assets/intake-view.html').read_text()
    # Single-pass substitution prevents source content from injecting template tokens.
    result=re.sub(r'__([A-Z_]+)__',lambda m:values[m[1]],template)
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(result)
    return {'found':sum(r[2]=='found' for r in rows),'external':sum(r[3]!='internal' for r in gaps),'internal':sum(r[3]=='internal' for r in gaps),'conflicts':sum(r[2]=='conflict' for r in rows)}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--run-dir',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    print(render(args.run_dir,args.output))
