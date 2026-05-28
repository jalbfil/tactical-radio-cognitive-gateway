from fastapi.testclient import TestClient
from app.main import app
client = TestClient(app)

def test_status_endpoint():
    response = client.get('/api/status')
    assert response.status_code == 200
    payload = response.json()
    assert 'classification' in payload
    assert 'decision' in payload

def test_set_jammed_scenario():
    response = client.post('/api/scenario/jammed_attack')
    assert response.status_code == 200
    payload = response.json()
    assert payload['scenario'] == 'jammed_attack'
    assert payload['classification']['state'] == 'JAMMED_ATTACK'
