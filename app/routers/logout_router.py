from fastapi import APIRouter, Request, Response, Depends
from app.services.logout_service import get_logout_service, LogoutService
from app.schemas.response_dto.auth_response import AuthLogoutResponse

router = APIRouter()

@router.post("/logout", response_model=AuthLogoutResponse)
async def logout(
    request: Request,  
    response: Response,
    logout_service: LogoutService = Depends(get_logout_service)
):
    return await logout_service.logout(request, response)
