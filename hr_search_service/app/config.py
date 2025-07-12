# app/config.py
from typing import List, Dict

# This dictionary simulates an organization-level configuration for displayed columns.
# The order of columns in the list determines their order in the API response.
ORGANIZATION_COLUMN_CONFIG: Dict[str, List[str]] = {
    # Configuration to match the image's columns for org_a
    "org_a": [
        "id", "first_name", "last_name", "email", "phone",
        "department", "position", "location", "status"
    ],
    "org_b": [
        "first_name", "last_name", "department", "location", "position", "status"
    ],
    # Add more organizations with their specific column configurations
    "org_c": [
        "first_name", "last_name", "email", "department", "position", "salary", "status" # Example: org_c can see salary
    ]
}

def get_organization_columns(organization_id: str) -> List[str]:
    """
    Retrieves the list of columns to be displayed for a given organization.

    Args:
        organization_id (str): The ID of the organization.

    Returns:
        List[str]: A list of column names. Returns an empty list if the organization
                   is not found in the configuration.
    """
    return ORGANIZATION_COLUMN_CONFIG.get(organization_id, [])

