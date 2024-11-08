# app/routers/user_router.py

from fastapi import APIRouter, HTTPException, Depends, Request
from app.services.user_updatename_service import UserService, get_user_service
from app.schemas.request_dto.user_updatename_request import UpdateUserNameRequest
from app.schemas.response_dto.user_updatename_response import UpdateUserNameResponse, UpdateProfileRes
from app.schemas.request_dto.user_updatename_request import UpdateUserProfileReq
from app.middleware.session.session_middleware import SessionMiddleware

router = APIRouter()

@router.put("/user/name/update", response_model=UpdateUserNameResponse)
async def update_user_name(request: UpdateUserNameRequest, service: UserService = Depends(get_user_service)):
    user_id = request.user_id
    new_name = request.new_name
    
    # 이름 업데이트 실행
    success = await service.update_user_name(user_id, new_name)
    if not success:
        raise HTTPException(status_code=500, detail="Updating user name failed")
    
    return UpdateUserNameResponse(message="User name updated successfully", user_id=user_id, new_name=new_name)

# 프로필 사진
@router.put("/profile")
async def update_profile_name(request: Request, post_input: UpdateUserProfileReq, service: UserService = Depends(get_user_service)):
    profile_url = post_input.profile_status
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")

    result = await service.update_profile(user_id, profile_url)

    return UpdateProfileRes(
        profile_url=profile_url
    )