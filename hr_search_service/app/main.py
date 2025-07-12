# main.py
from fastapi import FastAPI, HTTPException, Depends, Request, Query
from fastapi.responses import JSONResponse
from typing import List, Dict, Any, Optional

from app.models import Employee, SearchResponse
from app.database import get_employees
from app.config import get_organization_columns
from app.rate_limiter import rate_limiter, RATE_LIMIT_COUNT, RATE_LIMIT_WINDOW_SECONDS

app = FastAPI(
    title="HR Employee Search API",
    description="API for populating the employee search directory with dynamic columns and rate-limiting.",
    version="1.0.0",
    openapi_url="/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

def get_client_key(request: Request) -> str:
    """
    Determines the client key for rate limiting.
    Uses the client's IP address. In a production environment behind a proxy,
    you might need to look at 'X-Forwarded-For' or similar headers.
    """
    # For local development, client.host might be 'testclient' or '127.0.0.1'
    # In production, this would typically be the actual client IP.
    return request.client.host if request.client else "unknown_client"

@app.get(
    "/search",
    response_model=SearchResponse,
    summary="Search employees by various criteria with dynamic columns",
    description="""
    Searches for employee records within a specific organization.
    The returned columns are dynamically configured per organization.
    Includes rate-limiting to prevent API abuse.
    """,
    tags=["Employees"]
)
async def search_employees(
    request: Request,
    organization_id: str = Query(..., description="The ID of the organization to search within."),
    name: Optional[str] = Query(None, description="Partial or full name of the employee."),
    department: Optional[str] = Query(None, description="Department of the employee."),
    location: Optional[str] = Query(None, description="Location of the employee."),
    position: Optional[str] = Query(None, description="Position of the employee."),
) -> SearchResponse:
    """
    Handles the employee search request.

    Args:
        request (Request): The incoming FastAPI request object (used for client IP).
        organization_id (str): The ID of the organization. This is mandatory to prevent data leaks.
        name (Optional[str]): Filter by employee name.
        department (Optional[str]): Filter by employee department.
        location (Optional[str]): Filter by employee location.
        position (Optional[str]): Filter by employee position.

    Returns:
        SearchResponse: A list of employee dictionaries, with only the configured columns.

    Raises:
        HTTPException:
            - 429 Too Many Requests if rate limit is exceeded.
            - 404 Not Found if the organization ID is invalid or no columns are configured.
            - 500 Internal Server Error for unexpected issues.
    """
    client_key = get_client_key(request)

    # Apply rate limiting
    if not rate_limiter.check_limit(client_key):
        raise HTTPException(
            status_code=429,
            detail=f"Too many requests. Please try again after {RATE_LIMIT_WINDOW_SECONDS} seconds. "
                   f"Limit is {RATE_LIMIT_COUNT} requests per {RATE_LIMIT_WINDOW_SECONDS} seconds."
        )
    rate_limiter.record_request(client_key)

    # Get the configured columns for the organization
    allowed_columns = get_organization_columns(organization_id)
    if not allowed_columns:
        raise HTTPException(
            status_code=404,
            detail=f"Organization '{organization_id}' not found or no display columns configured."
        )

    # Simulate fetching employees from the database
    # In a real system, this would be an optimized database query.
    employees: List[Employee] = get_employees(
        organization_id=organization_id,
        name=name,
        department=department,
        location=location,
        position=position
    )

    # Prepare the response with dynamic columns
    response_employees: List[Dict[str, Any]] = []
    for emp in employees:
        employee_data = emp.model_dump() # Converts Pydantic model to dict
        filtered_data = {}
        for col in allowed_columns:
            if col in employee_data:
                filtered_data[col] = employee_data[col]
            # else: # Optionally, handle cases where a configured column might not exist in the model
            #     print(f"Warning: Column '{col}' configured for '{organization_id}' but not found in Employee model.")
        response_employees.append(filtered_data)

    return SearchResponse(employees=response_employees)

# You can run this file using: uvicorn main:app --reload
# Access the API documentation at http://127.0.0.1:8000/docs
