from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)

TEST_ACTIVITY = "Chess Club"
TEST_EMAIL = "pytest-user@example.com"


def setup_function():
    # Ensure clean state before each test
    participants = activities[TEST_ACTIVITY]["participants"]
    try:
        while TEST_EMAIL in participants:
            participants.remove(TEST_EMAIL)
    except Exception:
        pass


def teardown_function():
    # Clean up after tests
    participants = activities[TEST_ACTIVITY]["participants"]
    try:
        while TEST_EMAIL in participants:
            participants.remove(TEST_EMAIL)
    except Exception:
        pass


def test_root_redirect_serves_index():
    resp = client.get("/")
    assert resp.status_code == 200
    assert "Mergington High School" in resp.text


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert TEST_ACTIVITY in data
    assert "participants" in data[TEST_ACTIVITY]


def test_signup_and_prevent_duplicate():
    # Signup first time
    resp = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json().get("message", "")

    # Second signup should fail with 400
    resp2 = client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")
    assert resp2.status_code == 400
    assert "already signed up" in resp2.json().get("detail", "")


def test_remove_participant_success_and_not_found():
    # Ensure participant present
    if TEST_EMAIL not in activities[TEST_ACTIVITY]["participants"]:
        client.post(f"/activities/{TEST_ACTIVITY}/signup?email={TEST_EMAIL}")

    # Remove participant
    resp = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")
    assert resp.status_code == 200
    assert "Removed" in resp.json().get("message", "")

    # Attempt to remove again should return 404
    resp2 = client.delete(f"/activities/{TEST_ACTIVITY}/participants?email={TEST_EMAIL}")
    assert resp2.status_code == 404
    assert "Participant not found" in resp2.json().get("detail", "")
