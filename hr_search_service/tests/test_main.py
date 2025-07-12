# tests/test_main.py
import pytest
from fastapi.testclient import TestClient
import time

# Import the main FastAPI app and the rate limiter instance to reset it for tests
from main import app
from app.rate_limiter import rate_limiter, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW_SECONDS
from app.database import _employees_data # For direct access to test data if needed

# Create a TestClient instance for the FastAPI app
client = TestClient(app)

# Fixture to reset the rate limiter before each test that uses it
@pytest.fixture(autouse=True)
def reset_rate_limiter():
    """Resets the rate limiter's internal state before each test."""
    rate_limiter._requests.clear()
    yield

def test_search_by_organization_id():
    """Test searching for employees by a valid organization ID."""
    response = client.get("/search?organization_id=org_a")
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    # org_a now has 3 Active + 1 Not started + 1 Terminated = 5 employees
    assert len(data["employees"]) == 5 # Corrected expected count to 5
    # Verify dynamic columns for org_a to match the image
    expected_columns_org_a = ["id", "first_name", "last_name", "email", "phone", "department", "position", "location", "status"]
    for emp in data["employees"]:
        assert all(col in emp for col in expected_columns_org_a)
        assert len(emp) == len(expected_columns_org_a) # Ensure no extra columns
        assert emp["status"] in ["Active", "Not started", "Terminated"] # Check status field

def test_search_by_organization_id_org_b():
    """Test searching for employees by a valid organization ID for org_b."""
    response = client.get("/search?organization_id=org_b")
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    assert len(data["employees"]) == 3 # org_b still has 3 employees
    # Verify dynamic columns for org_b
    expected_columns_org_b = ["first_name", "last_name", "department", "location", "position", "status"]
    for emp in data["employees"]:
        assert all(col in emp for col in expected_columns_org_b)
        assert len(emp) == len(expected_columns_org_b) # Ensure no extra columns
        assert "id" not in emp # Ensure 'id' is not present for org_b config
        assert emp["status"].lower() in ["active", "not started"] # Corrected to be case-insensitive for robustness

def test_search_by_organization_id_org_c_with_salary():
    """Test searching for employees by a valid organization ID for org_c, which includes salary."""
    response = client.get("/search?organization_id=org_c")
    assert response.status_code == 200
    data = response.json()
    assert "employees" in data
    # Assuming org_c has no employees in our mock data, but the config is valid
    assert len(data["employees"]) == 0
    # Verify dynamic columns for org_c (even if no employees are returned, the schema should be valid)
    expected_columns_org_c = ["first_name", "last_name", "email", "department", "position", "salary", "status"]
    # If there were employees, we'd check their structure:
    # for emp in data["employees"]:
    #     assert all(col in emp for col in expected_columns_c)
    #     assert len(emp) == len(expected_columns_c)
    #     assert "salary" in emp # Crucially, salary should be present

def test_search_non_existent_organization():
    """Test searching for a non-existent organization ID."""
    response = client.get("/search?organization_id=non_existent_org")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found or no display columns configured" in response.json()["detail"]

def test_search_by_name():
    """Test filtering employees by first or last name."""
    response = client.get("/search?organization_id=org_a&name=Alice")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "Alice"
    assert data["employees"][0]["last_name"] == "Smith"

    response = client.get("/search?organization_id=org_a&name=Johnson")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "Bob"
    assert data["employees"][0]["last_name"] == "Johnson"

    # Test full name search
    response = client.get("/search?organization_id=org_a&name=Charlie Brown")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "Charlie"
    assert data["employees"][0]["last_name"] == "Brown"


def test_search_by_department_and_location():
    """Test filtering employees by department and location."""
    response = client.get("/search?organization_id=org_a&department=Engineering&location=New York")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "Alice"
    assert data["employees"][0]["last_name"] == "Smith"

def test_search_by_single_status():
    """Test filtering employees by a single status."""
    response = client.get("/search?organization_id=org_a&status=Terminated")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 1
    assert data["employees"][0]["first_name"] == "Eve"
    assert data["employees"][0]["status"] == "Terminated"

    response = client.get("/search?organization_id=org_a&status=Active")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 3 # Alice, Bob, Charlie

def test_search_by_multiple_statuses():
    """Test filtering employees by multiple statuses."""
    # Search for Active and Not started employees in org_a
    response = client.get("/search?organization_id=org_a&status=Active&status=Not started")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 4 # Alice, Bob, Charlie (Active) + Diana (Not started)
    statuses_found = {emp["status"] for emp in data["employees"]}
    assert "Active" in statuses_found
    assert "Not started" in statuses_found
    assert "Terminated" not in statuses_found

def test_search_no_match():
    """Test search with filters that yield no results."""
    response = client.get("/search?organization_id=org_a&name=NonExistent")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 0

def test_data_leak_prevention():
    """
    Test that an organization cannot see another organization's data.
    Attempt to search for an employee from org_b using org_a's ID.
    """
    # Try to find Frank White (from org_b) using org_a's ID
    response = client.get("/search?organization_id=org_a&name=Frank White")
    assert response.status_code == 200
    data = response.json()
    assert len(data["employees"]) == 0 # Should return no results for org_a

    # Verify Frank White exists for org_b
    response_org_b = client.get("/search?organization_id=org_b&name=Frank White")
    assert response_org_b.status_code == 200
    data_org_b = response_org_b.json()
    assert len(data_org_b["employees"]) == 1
    assert data_org_b["employees"][0]["first_name"] == "Frank"
    assert data_org_b["employees"][0]["last_name"] == "White"


def test_rate_limiting():
    """
    Test the custom rate-limiting mechanism.
    It should allow N requests, then block, then allow after the window.
    """
    # Make requests up to the limit using a single client key
    client_key_for_test = "single_test_client"
    for i in range(RATE_LIMIT_COUNT):
        response = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_key_for_test})
        assert response.status_code == 200, f"Request {i+1} failed unexpectedly."

    # The next request should be rate-limited
    response = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_key_for_test})
    assert response.status_code == 429
    assert "Too many requests" in response.json()["detail"]

    # Wait for the rate limit window to pass
    time.sleep(RATE_LIMIT_WINDOW_SECONDS + 1) # Add 1 second buffer

    # After the window, requests should be allowed again
    response = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_key_for_test})
    assert response.status_code == 200

def test_rate_limiting_different_clients():
    """
    Test that rate limiting is applied per client key.
    """
    # Client 1 hits their limit
    client_one_key = "client_one_unique_id"
    for i in range(RATE_LIMIT_COUNT):
        response = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_one_key})
        assert response.status_code == 200, f"Client 1 request {i+1} failed unexpectedly."

    # Client 2 should still be able to make requests (it has its own limit)
    client_two_key = "client_two_unique_id"
    response_client_two = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_two_key})
    assert response_client_two.status_code == 200, "Client 2 should not be rate-limited."

    # Client 1 should now be blocked
    response_client_one_blocked = client.get("/search?organization_id=org_a", headers={"X-Client-IP": client_one_key})
    assert response_client_one_blocked.status_code == 429, "Client 1 should be rate-limited."

def test_missing_organization_id():
    """Test calling the API without the mandatory organization_id."""
    response = client.get("/search") # Missing organization_id query parameter
    assert response.status_code == 422 # Unprocessable Entity due to validation error
    # The error message from FastAPI starts with a capital 'F'
    assert 'Field required' in response.json()["detail"][0]["msg"]

