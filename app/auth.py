import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from supermemory import Supermemory

# Initialize the Supermemory client
# This assumes the SUPERMEMORY_API_KEY is set in your .env file
supermemory_client = Supermemory(api_key="sm_qaJzZjFNjd7R6AajEnxgzW_XsYEdDMtGKhKlkAkvSwyhyfPyrjWFviOkqEtzXKbctVpjtZAVWUouqqcwTWwIHiq")

# Create a router to organize these endpoints
router = APIRouter()

# Pydantic model for request validation
class AuthRequest(BaseModel):
    user_id: str

def user_exists(user_id: str) -> bool:
    """
    A helper function that checks if a user has any memories in Supermemory.
    This is how we determine if a user account "exists".
    """
    try:
        # We only need to check for one memory to confirm existence
        memories = supermemory_client.get_memory(user_id=user_id, limit=1)
        return bool(memories)
    except Exception:
        # If an API error occurs (like a 404 for a non-existent user),
        # we can safely assume the user does not exist.
        return False

@router.post("/register")
async def register(request: AuthRequest):
    """
    Handles new user registration.
    It checks if the user already exists. If they do, it returns an error.
    If not, it creates a new "welcome" memory for them, effectively creating the account.
    """
    if user_exists(request.user_id):
        raise HTTPException(
            status_code=400, 
            detail="Username already exists. Please log in."
        )
    
    try:
        # Add a placeholder memory to "create" the user in Supermemory's system
        await supermemory_client.memories.add({
    
            "user_id": request.user_id
        })
        return {"status": "success", "message": "Registration successful. You can now log in."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")


@router.post("/login")
async def login(request: AuthRequest):
    """
    Handles user login.
    It checks if the user exists. If they don't, it returns an error
    prompting them to register first.
    """
    if not user_exists(request.user_id):
        raise HTTPException(
            status_code=404, 
            detail="Username not found. Please register first."
        )
    
    # If the user exists, the login is successful
    return {"status": "success", "user_id": request.user_id}