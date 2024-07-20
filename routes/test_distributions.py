from fastapi.testclient import TestClient

from ..main import app

client = TestClient(app)


def test_distributions_triangular():
    params = {"distMin": 200, "distMode": 400, "distMax": 600}
    response = client.get(
        "/api/distributions/triangular",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["distValues"]) == 1000


def test_distributions_uniform():
    params = {"distMin": 200, "distMax": 600}
    response = client.get(
        "/api/distributions/uniform",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["distValues"]) == 1000


def test_distributions_truncated_normal():
    params = {
        "distMin": 200,
        "distMean": 400,
        "distMax": 600,
        "distSD": 100,
    }
    response = client.get(
        "/api/distributions/truncated_normal",
        params=params,
    )
    assert response.status_code == 200
    assert len(response.json()["distValues"]) == 1000


def test_distributions_bootstrap():
    values = [200, 300, 400, 500, 600, 700, 800, 900, 1000, 1100]
    response = client.post(
        "/api/distributions/bootstrap",
        json={"values": values},
    )
    assert response.status_code == 200
    assert len(response.json()["bootstrapValues"]) == len(values)
