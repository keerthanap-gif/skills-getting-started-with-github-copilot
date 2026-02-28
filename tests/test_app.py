import copy

import pytest
from fastapi.testclient import TestClient

# import the module so we can reset its globals
import src.app as app_module

client = TestClient(app_module.app)

# keep an immutable copy of the original activities state
original_activities = copy.deepcopy(app_module.activities)


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Ensure each test starts with a fresh copy of the activities data.
    This fixture runs automatically for every test.
    """
    app_module.activities = copy.deepcopy(original_activities)
    yield


def test_get_activities():
    # Arrange: nothing to arrange beyond fixture reset

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == original_activities


def test_successful_signup():
    # Arrange
    activity = "Chess Club"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    # verify state changed
    assert email in app_module.activities[activity]["participants"]


def test_duplicate_signup_error():
    # Arrange
    activity = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{activity}/signup", params={"email": existing_email}
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_nonexistent_activity():
    # Arrange
    fake_activity = "Nonexistent"
    email = "someone@mergington.edu"

    # Act
    response = client.post(
        f"/activities/{fake_activity}/signup", params={"email": email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_successful_participant_removal():
    # Arrange
    activity = "Gym Class"
    to_remove = "john@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": to_remove}
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {to_remove} from {activity}"}
    # confirm the participant was removed
    assert to_remove not in app_module.activities[activity]["participants"]


def test_removal_of_nonexistent_participant():
    # Arrange
    activity = "Gym Class"
    fake_email = "ghost@mergington.edu"

    # Act
    response = client.delete(
        f"/activities/{activity}/participants", params={"email": fake_email}
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"
