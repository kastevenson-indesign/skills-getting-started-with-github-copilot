from src.app import activities


def test_root_redirects_to_static_index(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code in (302, 307)
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_all_activities(client):
    # Arrange
    expected_keys = {"description", "schedule", "max_participants", "participants"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert set(data) == set(activities)
    for details in data.values():
        assert set(details) == expected_keys


def test_signup_adds_participant(client):
    # Arrange
    activity_name = "Programming Class"
    email = "newstudent@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert email in activities[activity_name]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    participants_before = list(activities[activity_name]["participants"])

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"] == participants_before


def test_signup_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
    assert activity_name not in activities


def test_unregister_removes_participant(client):
    # Arrange
    activity_name = "Art Club"
    email = "painter@mergington.edu"
    activities[activity_name]["participants"].append(email)

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert email not in activities[activity_name]["participants"]


def test_unregister_participant_not_signed_up_returns_404(client):
    # Arrange
    activity_name = "Chess Club"
    email = "notsignedup@mergington.edu"
    participants_before = list(activities[activity_name]["participants"])

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"
    assert activities[activity_name]["participants"] == participants_before


def test_unregister_unknown_activity_returns_404(client):
    # Arrange
    activity_name = "Underwater Basket Weaving"
    email = "student@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/unregister", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
