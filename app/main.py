import os, sys, dotenv
dotenv.load_dotenv(encoding="utf-8")
sys.path.append(os.getenv("BACKEND_PATH"))

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 라우터, 서브앱
from routers.auth_router import router as auth_router
from routers.mainpage_router import router as mainpage_router
from routers.guestmode_router import router as guestmode_router
from routers.etc.sse_connection_router import router as sse_router
from routers.friend_router import router as friend_router

app = FastAPI()

app.add_middleware( # CORS 미들웨어 설정
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처를 허용합니다.
    allow_credentials=True,  # 쿠키를 포함한 요청을 허용합니다.
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다. 예: GET, POST, PUT, DELETE, PATCH 등
    allow_headers=["*"],  # 모든 헤더를 허용합니다.
)

app.include_router(auth_router, prefix="/auth", tags=["login"])
app.include_router(mainpage_router, prefix="/mainpage", tags=["mainpage"])
app.include_router(guestmode_router, prefix="/guestmode", tags=["guestmode"])
app.include_router(sse_router, prefix="/sse", tags=["sse"])
app.include_router(friend_router, prefix="/friend", tags=["friend"])

@app.get("/")
async def index():
    return {"message": "index page"}

if(__name__ == "__main__"):
    
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True) 