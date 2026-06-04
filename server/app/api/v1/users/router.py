from fastapi import APIRouter, Depends
from app.core.dependencies import get_current_active_user, get_current_admin_user
from app.models.user import User
from app.schemas.user import UserResponse
from app.schemas.response import APIResponse

router = APIRouter()

@router.get("/me", response_model=APIResponse[UserResponse])
async def get_me(
    current_user: User = Depends(get_current_active_user),
) -> APIResponse[UserResponse]:
    """Fetches the profile details of the currently authenticated active user."""
    return APIResponse(success=True, data=UserResponse.model_validate(current_user))

@router.get("/admin-only", response_model=APIResponse[dict])
async def admin_only_route(
    admin_user: User = Depends(get_current_admin_user),
) -> APIResponse[dict]:
    """Sample protected endpoint only accessible to users with the 'ADMIN' role."""
    return APIResponse(
        success=True,
        data={
            "message": f"Welcome Admin {admin_user.full_name}! You have successfully bypassed this authorization gate.",
            "role": admin_user.role,
        },
    )
