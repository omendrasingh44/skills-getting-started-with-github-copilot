import copy

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

ORIGINAL_ACTIVITIES = copy.deepcopy(activities)


@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the in-memory activity store before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    return TestClient(app)


def test_get_activities_returns_known_activity(client):
    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    body = response.json()
    assert "Chess Club" in body
    assert body["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"


def test_signup_adds_new_participant(client):
    # Arrange
    activity_name = "Chess Club"
    student_email = "newstudent@mergington.edu"
    initial_count = len(activities[activity_name]["participants"])

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": student_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {student_email} for {activity_name}"
    assert len(activities[activity_name]["participants"]) == initial_count + 1
    assert student_email in activities[activity_name]["participants"]


def test_duplicate_signup_returns_400(client):
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity_name}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up"


def test_delete_participant_removes_student(client):
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    assert participant_email in activities[activity_name]["participants"]

    # Act
    response = client.delete(
        f"/activities/{activity_name}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {participant_email} from {activity_name}"
    assert participant_email not in activities[activity_name]["participants"]
