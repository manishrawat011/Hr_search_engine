# Hr_search_engine

#HR Employee Search Microservice
This project implements a simple FastAPI microservice for an HR company, responsible for populating an employee search directory. It focuses on core backend functionalities, including dynamic column selection, custom rate-limiting, and robust data isolation, designed with performance considerations for large datasets.

**Table of Contents**
Overview
Features
Project Structure
Getting Started
Prerequisites
Local Setup and Run
Running with Docker
Running Tests

**Overview**
The primary goal of this microservice is to provide a highly performant and secure search API for employee data. It addresses key concerns such as dynamic output columns based on organizational configuration, protection against API abuse through rate-limiting, and strict data isolation to prevent cross-organizational data leaks.

**Note: This assignment focuses solely on the search API. CRUD operations for entities (Add employee, Import, Export) are explicitly out of scope and not implemented.**

**Features**

**Employee Search API (GET /search):**

Filters by organization_id (mandatory for data isolation).
Supports filtering by name (first or last name, partial match).
Supports filtering by department, location, position (exact match).
Supports filtering by status (e.g., "Active", "Not started", "Terminated"), including multiple status selections.

**Dynamic Columns:** Configurable at an organization level, allowing different organizations to display different sets and orders of columns in the search results.
**Custom Rate-Limiting:** An in-memory, custom-built rate-limiting system to prevent API spamming (no external libraries used for this).

**Data Leak Prevention:** Ensures that an organization's search queries only return data belonging to that specific organization and only the columns configured for them.

**Containerized:** Includes a Dockerfile for easy deployment.

**OpenAPI Specification**: Automatically generated API documentation (Swagger UI, Redoc).

**Unit Tested:** Comprehensive test suite covering functional and non-functional requirements.

**Project Structure**
hr_search_service/
├── Dockerfile
├── requirements.txt
├── main.py                 # Main FastAPI application
├── app/
│   ├── __init__.py         # Makes 'app' a Python package
│   ├── models.py           # Pydantic models for Employee and API Response
│   ├── database.py         # Simulated database (in-memory data and filtering logic)
│   ├── config.py           # Dynamic column configuration per organization
│   └── rate_limiter.py     # Custom in-memory rate-limiting implementation
└── tests/
    ├── __init__.py         # Makes 'tests' a Python package
    └── test_main.py        # Unit tests for the FastAPI application

**Getting Started**
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

**Prerequisites**
Python 3.8+

Docker Desktop (for containerized setup)

pip (Python package installer)

Local Setup and Run

**1. Clone the repository:**

git clone <your-github-repo-link>
cd hr_search_service

**Install dependencies:**

pip install -r requirements.txt

**Run the FastAPI application:**

uvicorn main:app --reload --host 0.0.0.0 --port 8000

**The --reload flag is useful during development as it restarts the server on code changes.
The API will be accessible at http://localhost:8000.**

Running with Docker
1. Ensure Docker Desktop is running.

2 . Navigate to the project root directory: cd hr_search_service

3. Build the Docker image: docker build -t hr-search-api .

4. Run the Docker container: docker run -p 8000:8000 hr-search-api

**The API will be accessible at http://localhost:8000.**

**Running Tests**
While in the project root directory and with your virtual environment activated (or within the Docker container's build process), run: **pytest**

This will execute all unit tests located in the tests/ directory.

**API Documentation**
Once the application is running (either locally or via Docker), you can access the interactive API documentation:

**Swagger UI: http://localhost:8000/docs
Redoc: http://localhost:8000/redoc**

You can use the "Try it out" feature in Swagger UI to make direct API calls and see the responses.

**Example API Calls:**

**Get all employees for org_a:**
http://localhost:8000/search?organization_id=org_a

**Filter org_a employees by department:**
http://localhost:8000/search?organization_id=org_a&department=Engineering

**Filter org_a employees by name (partial match):**
http://localhost:8000/search?organization_id=org_a&name=Alice
http://localhost:8000/search?organization_id=org_a&name=Charlie%20Brown

**Filter org_a employees by a single status:**
http://localhost:8000/search?organization_id=org_a&status=Terminated

**Filter org_a employees by multiple statuses:**
http://localhost:8000/search?organization_id=org_a&status=Active&status=Not%20started

**Design Decisions**
**FastAPI Framework**: Chosen for its high performance, ease of use, and automatic generation of OpenAPI documentation, which is crucial for API discoverability and consumption.

**Modular Architecture**: The codebase is split into logical modules (models, database, config, rate_limiter) to enhance readability, maintainability, and testability.

**Simulated Database (app/database.py):** For this assignment, employee data is stored in memory. In a production environment, this would be replaced by an actual relational database (e.g., PostgreSQL) with an ORM (like SQLAlchemy) and proper indexing for performance. The organization_id is a primary filter to simulate efficient sharding/partitioning.

**Custom Rate-Limiting (app/rate_limiter.py):** Implemented from scratch using Python's standard library, as per the assignment's constraint. It's an in-memory, sliding window counter.

**Scalability Note:** For a highly available and scalable production system, this in-memory solution would need to be replaced by a distributed, persistent store (e.g., Redis) to ensure consistent rate limits across multiple API instances.

**Dynamic Column Configuration (app/config.py):** A dictionary maps organization_id to a list of allowed columns. This demonstrates flexibility in API response structure without altering the core data model. In a real system, this configuration might reside in a dedicated configuration service or a database table.

**Data Leak Prevention:**

The organization_id is a mandatory query parameter and is strictly enforced at the data retrieval layer (get_employees).

The API response is dynamically filtered to include only the columns explicitly configured for the requesting organization, preventing exposure of sensitive or irrelevant data (e.g., salary unless specifically allowed).

Error Handling: FastAPI's HTTPException is used to return appropriate HTTP status codes (e.g., 429 Too Many Requests, 404 Not Found, 422 Unprocessable Entity) for better API client communication.

**Assignment Notes**
No external libraries were used for rate-limiting, adhering to the assignment's specific constraint.

The database.py module is a mock and does not involve actual database migrations or complex ORM setups, focusing on the API logic as requested.

The application is designed to be purely backend, with no frontend components.

The name filter now searches across both first_name and last_name fields, supporting partial matches on either or the full name.

The status filter now accepts multiple values, mirroring the UI's multi-select checkboxes.
