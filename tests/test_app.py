import copy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


client = TestClient(app)


@pytest.fixture(autouse=True)
def restore_activities():
    snapshot = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(snapshot)


def test_get_activities_returns_activity_list():
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()
    assert "Gym Class" in data
    assert data["Gym Class"]["max_participants"] == 30


def test_signup_adds_participant():
    response = client.post(
        "/activities/Gym%20Class/signup",
        params={"email": "gym@gmail.com"},
    )

    assert response.status_code == 200
    assert "gym@gmail.com" in activities["Gym Class"]["participants"]


def test_signup_rejects_duplicate_participant():
    response = client.post(
        "/activities/Gym%20Class/signup",
        params={"email": "john@mergington.edu"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_rejects_unknown_activity():
    response = client.post(
        "/activities/Unknown/signup",
        params={"email": "someone@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_remove_participant_removes_from_activity():
    response = client.delete(
        "/activities/Gym%20Class/participants",
        params={"email": "john@mergington.edu"},
    )

    assert response.status_code == 200
    assert "john@mergington.edu" not in activities["Gym Class"]["participants"]


def test_remove_participant_rejects_missing_participant():
    response = client.delete(
        "/activities/Gym%20Class/participants",
        params={"email": "missing@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
