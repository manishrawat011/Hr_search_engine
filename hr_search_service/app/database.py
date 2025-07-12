# app/database.py
from typing import List, Dict, Any, Optional
from app.models import Employee

# In a real application, this would be a database connection and ORM queries.
# We're simulating a database with in-memory data for this assignment.

# Sample Employee Data (simulating millions of users for demonstration)
# This data is carefully crafted to allow testing of organization-specific data leaks
# and various filter options.
_employees_data: List[Employee] = [
    # Organization A Employees
    Employee(
        id="emp001", organization_id="org_a", first_name="Alice", last_name="Smith", email="alice.s@orga.com",
        phone="111-222-3333", department="Engineering", location="New York",
        position="Software Engineer", status="Active", salary=90000.00
    ),
    Employee(
        id="emp002", organization_id="org_a", first_name="Bob", last_name="Johnson", email="bob.j@orga.com",
        phone="111-222-4444", department="HR", location="New York",
        position="HR Manager", status="Active", salary=85000.00
    ),
    Employee(
        id="emp003", organization_id="org_a", first_name="Charlie", last_name="Brown", email="charlie.b@orga.com",
        phone="111-222-5555", department="Engineering", location="San Francisco",
        position="Senior Software Engineer", status="Active", salary=120000.00
    ),
    Employee(
        id="emp004", organization_id="org_a", first_name="Diana", last_name="Prince", email="diana.p@orga.com",
        phone="111-222-6666", department="Marketing", location="New York",
        position="Marketing Specialist", status="Not started", salary=70000.00
    ),
    Employee(
        id="emp005", organization_id="org_a", first_name="Eve", last_name="Adams", email="eve.a@orga.com",
        phone="111-222-7777", department="Sales", location="Chicago",
        position="Sales Representative", status="Terminated", salary=75000.00
    ),
    # Organization B Employees
    Employee(
        id="emp006", organization_id="org_b", first_name="Frank", last_name="White", email="frank.w@orgb.com",
        phone="222-333-1111", department="Engineering", location="London",
        position="DevOps Engineer", status="Active", salary=95000.00
    ),
    Employee(
        id="emp007", organization_id="org_b", first_name="Grace", last_name="Black", email="grace.b@orgb.com",
        phone="222-333-2222", department="HR", location="London",
        position="HR Coordinator", status="Active", salary=60000.00
    ),
    Employee(
        id="emp008", organization_id="org_b", first_name="Heidi", last_name="Green", email="heidi.g@orgb.com",
        phone="222-333-3333", department="Finance", location="Berlin",
        position="Accountant", status="Not started", salary=70000.00
    ),
]


def get_employees(
        organization_id: str,
        name: str = None,  # This parameter will now search across first_name and last_name
        department: str = None,
        location: str = None,
        position: str = None,
        statuses: Optional[List[str]] = None  # Changed to accept a list of statuses
) -> List[Employee]:
    """
    Simulates fetching employees from a database based on organization ID and filters.
    In a real scenario, this would involve optimized database queries (e.g., SQL WHERE clauses
    with appropriate indexes on organization_id, name, department, location, position).

    Args:
        organization_id (str): The ID of the organization to filter by (mandatory for data isolation).
        name (str, optional): Filter by employee first or last name (case-insensitive, partial match).
        department (str, optional): Filter by department (case-insensitive, exact match).
        location (str, optional): Filter by location (case-insensitive, exact match).
        position (str, optional): Filter by position (case-insensitive, exact match).
        statuses (Optional[List[str]]): Filter by a list of employment statuses (case-insensitive, exact match).

    Returns:
        List[Employee]: A list of Employee objects matching the criteria.
    """
    results: List[Employee] = []
    name_lower = name.lower() if name else None
    department_lower = department.lower() if department else None
    location_lower = location.lower() if location else None
    position_lower = position.lower() if position else None

    # Convert provided statuses to lowercase for case-insensitive comparison
    statuses_lower = [s.lower() for s in statuses] if statuses else None

    # First and foremost, filter by organization_id to prevent data leaks.
    # This is critical for performance in a real DB with sharding/partitioning.
    org_filtered_employees = [
        emp for emp in _employees_data if emp.organization_id == organization_id
    ]

    for employee in org_filtered_employees:
        match = True

        # New logic for name filtering: check against full name
        if name_lower:
            full_name_lower = f"{employee.first_name} {employee.last_name}".lower()
            if name_lower not in full_name_lower:
                match = False

        if department_lower and department_lower != employee.department.lower():
            match = False
        if location_lower and location_lower != employee.location.lower():
            match = False
        if position_lower and position_lower != employee.position.lower():
            match = False

        # Check if employee's status is in the list of provided statuses
        if statuses_lower and employee.status.lower() not in statuses_lower:
            match = False

        if match:
            results.append(employee)

    # In a real scenario with millions of users, direct iteration like this would be slow.
    # Database indexes and proper query optimization would be essential.
    # For full-text search on names, a dedicated search engine (e.g., Elasticsearch)
    # or database-specific full-text search capabilities would be used.

    return results

