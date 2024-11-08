# logout_service.py
import requests
from fastapi import Request, Response, HTTPException, status
from typing import Optional
from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.utils.db_handlers.redis_handler import RedisHandler
from app.deps import get_session_coll, get_session_cache


class LogoutService:
    def __init__(self, 
                 session_coll: Optional[MongoDBHandler] = None,
                 session_cache: Optional[RedisHandler] = None):
        self.session_coll = session_coll if session_coll else get_session_coll()
        self.session_cache = session_cache if session_cache else get_session_cache()

    async def logout(self, request: Request, response: Response) -> dict:
        # 쿠키에서 세션 id를 가져옴
        print("logout1")
        print(request)
        print(request.cookies)
        session_id = request.cookies.get("session_id")
        print("logout2")
        # if not session_id:
        #     raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No session_id in cookie")
        print("logout3")
        # redis, mongoDB에서 세션 조회
        session_data = await self.session_cache.select(session_id)
        print(session_data)
        if session_data != False:
            session_data = await self.session_coll.select({"_id": session_id})
        #     if not session_data:
        #         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid session")

        print("logout4", session_data)
        # redis와 mongoDB에서 세션 삭제
        await self.session_cache.delete(session_id)
        await self.session_coll.delete({"_id": session_id})
        print("logout5")
        # 구글 로그아웃 처리
        # if session_data.get("provider") == "google":
        print("logout6")
        token = session_data.get("access_token")
        print("ㄴㅇㄹㄴㅇㅁㄹㄴㅇㄴㄹㅇㅁㅁㄴㄹㅇ , ", token )
        self.google_logout(token)
        # if token:
        #     requests.get(f"https://accounts.google.com/o/oauth2/revoke?token={token}")
        # 카카오 로그아웃 처리
        # elif session_data.get("provider") == "kakao":
        print("logout7")
        self.kakao_logout(token)
        # headers = {
        #     "Authorization": f"Bearer {token}"
        # }

        # 쿠키 삭제
        request.cookies.clear()
        response.delete_cookie(key="session_id")

        
        print("logout9")

        return {"message": "Logout successful"}

    # token 이 none이 나옴
    def google_logout(self, token):
        if token:
            requests.get(f"https://accounts.google.com/o/oauth2/revoke?token={token}")
        print("googlelogout1")

    def kakao_logout(self, token):
        print("token!!!!!!kakao!!!!!!!")
        print(token)
        if token:
            print("kakaologout1")
            headers = {
                "Authorization": f"Bearer {token}"
            }
            # 원래 뭐더라
            a = requests.get("https://kapi.kakao.com/v1/user/logout", headers=headers)
            print("kakaologout2")
            print(a.json())
            print(a.status_code)


def get_logout_service() -> LogoutService:
    return LogoutService()