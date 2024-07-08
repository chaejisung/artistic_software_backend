import uvicorn
from fastapi import FastAPI

from config.config import settings
from api.middleware.session_middleware import SessionMiddleware
from api.rest.login.login_google import router as login_google_router
from api.rest.login.login_kakao import router as login_kakao_router
from api.rest.mainpage.mainpage import sub_app as mainpage_app
from api.rest.personalspace.personalspace import sub_app as personalspace_app, router as personalspace_router

app = FastAPI()

# # 미들웨어 등록
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)

# 라우터 등록
app.include_router(login_google_router, prefix="/auth/google", tags=["google", "login"])
app.include_router(login_kakao_router, prefix="/auth/kakao", tags=["kakao", "login"])
app.include_router(personalspace_router, prefix="/personalspace", tags=["personalspace"])

# 서브 앱 등록
app.mount(path="/mainpage", app=mainpage_app)
app.mount(path="/personalspace", app=personalspace_app)

# 로그인 화면
@app.get("/")
async def index():
    return {"message": "Login Page"}

if(__name__ == "__main__"):
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)