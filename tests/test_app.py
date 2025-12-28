import copy
import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    # Import inside fixture to avoid any top-level side-effects at collection time
    from src.app import app
    with TestClient(app) as c:
        yield c


@pytest.fixture
def activities_snapshot():
    # snapshot and restore activities between tests to avoid cross-test pollution
    from src.app import activities
    snap = copy.deepcopy(activities)
    yield activities
    activities.clear()
    activities.update(snap)


def test_get_activities_returns_activities(client):
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_and_unregister_participant(client, activities_snapshot):
    from src.app import activities
    activity = "Programming Class"
    test_email = "test.user@example.com"

    # ensure clean state
    if test_email in activities[activity]["participants"]:
        activities[activity]["participants"].remove(test_email)

    # signup
    resp = client.post(f"/activities/{activity}/signup?email={test_email}")
    assert resp.status_code == 200
    assert test_email in activities[activity]["participants"]

    # unregister
    resp2 = client.delete(f"/activities/{activity}/participant?email={test_email}")
    assert resp2.status_code == 200
    assert test_email not in activities[activity]["participants"]
