import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

INITIAL_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activities = ["Chess Club", "Programming Class"]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    for activity_name in expected_activities:
        assert activity_name in data


def test_signup_for_activity_adds_participant():
    # Arrange
    activity = "Chess Club"
    new_email = "testuser@example.com"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {new_email} for {activity}"

    activities_response = client.get("/activities")
    assert new_email in activities_response.json()[activity]["participants"]


def test_signup_duplicate_returns_error():
    # Arrange
    activity = "Chess Club"
    duplicate_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity}/signup?email={duplicate_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_remove_participant_from_activity():
    # Arrange
    activity = "Chess Club"
    participant = "daniel@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={participant}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {participant} from {activity}"

    activities_response = client.get("/activities")
    assert participant not in activities_response.json()[activity]["participants"]


def test_remove_nonexistent_participant_returns_404():
    # Arrange
    activity = "Chess Club"
    missing_email = "notfound@example.com"

    # Act
    response = client.delete(f"/activities/{activity}/participants?email={missing_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found"
