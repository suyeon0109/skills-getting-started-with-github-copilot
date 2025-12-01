
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities
import copy

client = TestClient(app)

# 초기 상태 백업
_initial_activities = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # 각 테스트 전 activities를 초기 상태로 리셋
    activities.clear()
    for k, v in _initial_activities.items():
        activities[k] = copy.deepcopy(v)

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data

def test_signup_for_activity():
    email = "pytestuser@mergington.edu"
    activity = "Chess Club"
    # Ensure not already signed up
    client.delete(f"/activities/{activity}/participants/{email}")
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert f"Signed up {email} for {activity}" in response.json()["message"]
    # Duplicate signup should fail
    response2 = client.post(f"/activities/{activity}/signup?email={email}")
    assert response2.status_code == 400
    # Clean up
    client.delete(f"/activities/{activity}/participants/{email}")

def test_remove_participant():
    email = "pytestremove@mergington.edu"
    activity = "Programming Class"
    # Add first
    signup_resp = client.post(f"/activities/{activity}/signup?email={email}")
    assert signup_resp.status_code == 200
    # 실제로 추가되었는지 확인
    activities_resp = client.get("/activities")
    assert activities_resp.status_code == 200
    participants = activities_resp.json()[activity]["participants"]
    assert email in participants
    # 삭제
    response = client.delete(f"/activities/{activity}/participants/{email}")
    assert response.status_code == 204
    # Remove again should 404
    response2 = client.delete(f"/activities/{activity}/participants/{email}")
    assert response2.status_code == 404
