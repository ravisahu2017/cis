import os
from fastapi import Security, HTTPException, status
from fastapi.security import APIKeyHeader

API_KEY_NAME = "X-API-Key"
USER_NAME = "X-User-Name"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)
user_name_header = APIKeyHeader(name=USER_NAME, auto_error=False)
def verify_api_key(api_key: str = Security(api_key_header), user_name: str = Security(user_name_header)):
    """
    Verify the API key provided in the request headers.
    Set CIS_API_KEY in your .env file to configure this.
    """
    expected_api_key = os.getenv("CIS_API_KEY")
    usernames = os.getenv("CIS_USER_NAMES").split(",")
    
    if not api_key:
        missing_header(API_KEY_NAME)
    if not user_name:
        missing_header(USER_NAME)

    if user_name not in usernames:
        invalid_header(USER_NAME)
    if api_key != expected_api_key:
        invalid_header(API_KEY_NAME)
    
    return api_key, user_name


def missing_header(header_name: str) -> HTTPException:
    """Raise HTTPException for missing header."""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"{header_name} header is missing",
    )

def invalid_header(header_name: str) -> HTTPException:
    """Raise HTTPException for invalid header."""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"{header_name} header is invalid",
    )