from fastapi.testclient import TestClient

from src.app import activities, app


client = TestClient(app)


def reset_activity_state(activity_name: str, participants=None):
    activities[activity_name]["participants"] = participants if participants is not None else []


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_names = [
        "Chess Club",
        "Programming Class",
        "Gym Class",
        "Soccer Team",
        "Basketball Team",
        "Drama Club",
        "Art Club",
        "Math Olympiad",
        "Science Club",
    ]

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert list(response.json().keys()) == expected_activity_names


def test_signup_adds_student_for_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"
    reset_activity_state(activity_name)

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_student():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"
    reset_activity_state(activity_name, [email])

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_returns_404_for_unknown_activity():
    # Arrange
    activity_name = "Not Real Club"
    email = "student@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_student_from_activity():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"
    reset_activity_state(activity_name, [email])

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Removed {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_unregister_returns_404_when_student_not_signed_up():
    # Arrange
    activity_name = "Soccer Team"
    email = "student@example.com"
    reset_activity_state(activity_name)

    # Act
    response = client.delete(f"/activities/{activity_name}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
