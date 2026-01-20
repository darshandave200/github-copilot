"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the /activities endpoint"""

    def test_get_activities_returns_200(self):
        """Test that /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self):
        """Test that /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_activities_have_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_list_contains_expected_activities(self):
        """Test that the activities list contains expected activities"""
        response = client.get("/activities")
        activities = response.json()

        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Music Band",
            "Debate Team",
            "Robotics Club",
        ]

        for activity in expected_activities:
            assert activity in activities


class TestSignupEndpoint:
    """Tests for the /activities/{activity_name}/signup endpoint"""

    def test_signup_new_student_returns_200(self):
        """Test signing up a new student returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_new_student_returns_success_message(self):
        """Test signup returns success message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent2@mergington.edu"
        )
        assert "message" in response.json()
        assert "newstudent2@mergington.edu" in response.json()["message"]

    def test_signup_adds_participant_to_activity(self):
        """Test that signup actually adds the participant"""
        email = "teststudent@mergington.edu"
        client.post(f"/activities/Programming%20Class/signup?email={email}")

        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Programming Class"]["participants"]

    def test_signup_duplicate_student_returns_400(self):
        """Test signing up the same student twice returns 400"""
        email = "duplicate@mergington.edu"
        # First signup
        response1 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response1.status_code == 200

        # Second signup should fail
        response2 = client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self):
        """Test signing up for nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_returns_200(self):
        """Test unregistering an existing participant returns 200"""
        email = "unregister@mergington.edu"
        # First sign up
        client.post(f"/activities/Chess%20Club/signup?email={email}")

        # Then unregister
        response = client.post(
            f"/activities/Chess%20Club/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes the participant"""
        email = "removeme@mergington.edu"
        # Sign up
        client.post(f"/activities/Tennis%20Club/signup?email={email}")

        # Verify they're signed up
        response = client.get("/activities")
        assert email in response.json()["Tennis Club"]["participants"]

        # Unregister
        client.post(f"/activities/Tennis%20Club/unregister?email={email}")

        # Verify they're removed
        response = client.get("/activities")
        assert email not in response.json()["Tennis Club"]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self):
        """Test unregistering non-existent participant returns 400"""
        response = client.post(
            "/activities/Chess%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_returns_404(self):
        """Test unregistering from nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]

    def test_unregister_returns_success_message(self):
        """Test unregister returns success message"""
        email = "successmsg@mergington.edu"
        # Sign up first
        client.post(f"/activities/Art%20Studio/signup?email={email}")

        # Unregister
        response = client.post(
            f"/activities/Art%20Studio/unregister?email={email}"
        )
        assert "message" in response.json()
        assert email in response.json()["message"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_redirects_to_static(self):
        """Test that root endpoint redirects to static index"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
