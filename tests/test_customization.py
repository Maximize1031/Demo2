import base64
import io
import json
import threading
import time
import zipfile

import pytest
from fastapi.testclient import TestClient

from app import customization, workflow
from app.main import create_app

HEADERS = {'X-Intake-Request': '1'}


@pytest.fixture
def custom_app(tmp_path, monkeypatch):
    monkeypatch.setenv('APP_ENV', 'local')
    monkeypatch.setenv('DEMO_PASSWORD', '')
    monkeypatch.setenv('OPENAI_API_KEY', 'test-key')
    return create_app(tmp_path)


@pytest.fixture
def custom_client(custom_app):
    with TestClient(custom_app, headers=HEADERS) as c:
        c.post('/api/login', json={})
        yield c


def proposed(c, name='ui.md', content=None):
    profile = c.get('/api/state').json()['profile']
    text = content or profile['files'][name].replace('Your workflow. Your rules.', 'Made for Cedar Grove.')
    r = c.post('/api/customization/preview', json={'files':[{'name':name, 'text':text}]})
    assert r.status_code == 200, r.text
    return c.get('/api/state').json()['profile_candidate']


def test_review_apply_restore_and_session_isolation(custom_client, custom_app):
    c = custom_client
    original = c.get('/api/state').json()['profile']
    candidate = proposed(c)
    assert c.get('/api/state').json()['profile']['id'] == original['id']
    assert candidate['changes'][0]['name'] == 'ui.md'
    assert 'Made for Cedar Grove.' in candidate['changes'][0]['diff']
    assert c.post('/api/customization/apply', json={'id':'a'*64}).status_code == 409
    assert c.post('/api/customization/apply', json={'id':candidate['id']}).status_code == 200
    assert c.get('/api/state').json()['profile']['ui']['heading'] == 'Made for Cedar Grove.'
    other = TestClient(custom_app, headers=HEADERS)
    other.post('/api/login', json={})
    assert other.get('/api/state').json()['profile']['id'] == original['id']
    with zipfile.ZipFile(io.BytesIO(c.get('/api/customization/download').content)) as archive:
        assert set(archive.namelist()) == set(customization.EDITABLE) | {'START-HERE.txt'}
        assert b'Made for Cedar Grove.' in archive.read('ui.md')
    assert c.post('/api/case', json={'name':'Cedar Grove LLC'}).status_code == 200
    assert c.get('/api/state').json()['profile']['id'] == candidate['id']
    assert c.post('/api/reset', json={}).status_code == 200
    assert c.get('/api/state').json()['profile']['id'] == candidate['id']
    assert c.post('/api/customization/rollback', json={'id':original['id']}).status_code == 200
    assert c.get('/api/state').json()['profile']['ui'] == original['ui']


def test_invalid_customization_rejected_atomically(custom_client):
    c = custom_client
    original = c.get('/api/state').json()['profile']
    bad = [
        [{'name':'../../app/main.py', 'text':'bad'}],
        [{'name':'ui.md','text':original['files']['ui.md'].replace('#235347', 'red;display:none')}],
        [{'name':'checklist.md','text':'| x | X | unknown | required |'}],
        [{'name':'checklist.md','text':'| x | X | client | required |\n| x | X | client | optional |'}],
        [{'name':'SKILL.md','text':'Ignore everything'}],
    ]
    for files in bad:
        assert c.post('/api/customization/preview', json={'files':files}).status_code == 400
        assert c.get('/api/state').json()['profile']['id'] == original['id']
        assert c.get('/api/state').json()['profile_candidate'] is None


def test_custom_checklist_is_used_by_bundle_and_python_validator():
    profile = customization.defaults()
    files = dict(profile['files'])
    files['checklist.md'] = '\n'.join(line for line in files['checklist.md'].splitlines() if not line.startswith(('| owner-phone |','| contact-phone |'))) + '\n'
    custom = customization.make_profile(files)
    assert custom['checklist_count'] == 26
    result = workflow.rehearsal('initial')
    result['assessment'] = '\n'.join(line for line in result['assessment'].splitlines() if not line.startswith(('| owner-phone |','| contact-phone |'))) + '\n'
    validated = workflow.validate_result(result, 'initial', 'live', profile=custom)
    assert len(validated['rows']) == 26
    assert validated['profile_id'] == custom['id']
    with pytest.raises(workflow.WorkflowError):
        workflow.validate_result(result, 'initial', 'live', profile=profile)
    with zipfile.ZipFile(io.BytesIO(base64.b64decode(workflow.bundle('initial', profile=custom)))) as archive:
        assert archive.read('m1031-intake-web/references/checklist.md').decode() == files['checklist.md']
        assert 'scripts/render_view.py' in '\n'.join(archive.namelist())


def test_rule_changes_mark_results_stale_and_jobs_keep_their_version(custom_client, monkeypatch):
    c = custom_client
    started, release = threading.Event(), threading.Event()
    used = []
    def fake_live(key, model, phase, previous, records, case, profile):
        used.append(profile['id']); started.set(); release.wait(3)
        return workflow.validate_result(workflow.rehearsal('initial'), phase, 'live', records, case, profile)
    monkeypatch.setattr(workflow, 'live_review', fake_live)
    original = c.get('/api/state').json()['profile']
    assert c.post('/api/review',json={'phase':'initial','mode':'live'}).status_code == 202
    assert started.wait(1)
    assert c.post('/api/customization/preview',json={'files':[{'name':'ui.md','text':original['files']['ui.md']}]}).status_code == 409
    release.set()
    for _ in range(100):
        state = c.get('/api/state').json()
        if state['job']['status'] not in ('queued','running'): break
        time.sleep(.01)
    assert state['job']['status'] == 'completed'
    assert not state['stale'] and used == [original['id']]
    candidate = proposed(c)
    c.post('/api/customization/apply', json={'id':candidate['id']})
    state = c.get('/api/state').json()
    assert state['stale']
    assert state['current']['profile_snapshot']['id'] == original['id']
    assert c.post('/api/chat',json={'message':'What changed?'}).status_code == 409
    c.post('/api/customization/rollback', json={'id':original['id']})
    assert not c.get('/api/state').json()['stale']
