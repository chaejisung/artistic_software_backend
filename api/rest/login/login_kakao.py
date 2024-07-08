import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
import httpx
from api.schema.schemas import LoginUser
from utils.session import create_session, get_current_user
from config.config import settings

router = APIRouter()


@router.get("/login")
async def login():
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize?client_id={settings.KAKAO_CLIENT_ID}"
        f"&redirect_uri={settings.KAKAO_REDIRECT_URI}&response_type=code"
    )
    return RedirectResponse(kakao_auth_url)


@router.get("/callback")
async def callback(request: Request):
    code = request.query_params.get("code")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code not found")

    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "client_secret": settings.KAKAO_CLIENT_SECRET,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            },
        )
        token_data = token_response.json()
        
        if "error" in token_data:
            raise HTTPException(status_code=400, detail=token_data["error_description"])

        user_response = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {token_data['access_token']}"},
        )
        user_data = user_response.json()

        if "kakao_account" not in user_data or "email" not in user_data["kakao_account"]:
            raise HTTPException(status_code=400, detail="Email not found in user data")
        if "properties" not in user_data or "nickname" not in user_data["properties"]:
            raise HTTPException(status_code=400, detail="Nickname not found in user data")
            
        user = LoginUser(
            id=user_data["id"],
            email=user_data["kakao_account"]["email"],
            name=user_data["properties"]["nickname"],
        )

        create_session(request, user)

    return JSONResponse(content={"message": "Login Success"})


@router.get("/me", response_model=LoginUser)
def me(user: LoginUser = Depends(get_current_user)):
    return user
