# app/models.py
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class Employee(BaseModel):
    """
    Represents an employee record.
    Includes sensitive fields (like salary) that should not be exposed by default,
    demonstrating data leak prevention through dynamic column selection.
    """
    id: str = Field(..., description="Unique identifier for the employee")
    organization_id: str = Field(..., description="ID of the organization the employee belongs to")
    first_name: str = Field(..., description="First name of the employee")
    last_name: str = Field(..., description="Last name of the employee")
    email: str = Field(..., description="Employee's email address")
    phone: Optional[str] = Field(None, description="Employee's phone number")
    department: str = Field(..., description="Department the employee works in")
    location: str = Field(..., description="Location of the employee's office")
    position: str = Field(..., description="Employee's job position")
    # Status values now align with the filter image: "Active", "Not started", "Terminated"
    status: str = Field(..., description="Employee's employment status (e.g., Active, Not started, Terminated)")
    # This field is intentionally included to demonstrate data leak prevention.
    # It should not be returned unless explicitly configured via dynamic columns.
    salary: float = Field(..., description="Employee's annual salary (sensitive information)")

class SearchResponse(BaseModel):
    """
    Represents the structure of the search API response.
    It's a list of dictionaries, where each dictionary represents an employee
    with only the dynamically selected columns.
    """
    employees: List[Dict[str, Any]] = Field(..., description="List of employee records with dynamic columns")

