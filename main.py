import uvicorn
from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from config.config import settings
from api.middleware.session_middleware import SessionMiddleware
from api.rest.login.login_google import router as login_google_router
from api.rest.login.login_kakao import router as login_kakao_router
from api.rest.mainpage.mainpage import sub_app as mainpage_app
from api.rest.personalspace.personalspace import sub_app as personalspace_app, router as personalspace_router
from utils.session_manage import session_manager, scheduler_shutdown

# 시작 시 스케줄링
@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup 이벤트 
    await session_manager()
    print("startup event 실행 완료")
    
    yield  # 제어권 넘기기
    
    # shutdown 이벤트 
    await scheduler_shutdown()
    print("shutdown event 실행 완료")

app = FastAPI(lifespan=lifespan)

# # 미들웨어 등록
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)
app.add_middleware( # CORS 미들웨어 설정
    CORSMiddleware,
    allow_origins=["*"],  # 모든 출처를 허용합니다.
    allow_credentials=True,  # 쿠키를 포함한 요청을 허용합니다.
    allow_methods=["*"],  # 모든 HTTP 메소드를 허용합니다. 예: GET, POST, PUT, DELETE, PATCH 등
    allow_headers=["*"],  # 모든 헤더를 허용합니다.
)

# 라우터 등록
app.include_router(login_google_router, prefix="/auth/google", tags=["google", "login"])
app.include_router(login_kakao_router, prefix="/auth/kakao", tags=["kakao", "login"])
app.include_router(personalspace_router, prefix="/personal", tags=["personal"])

# 서브 앱 등록
app.mount(path="/mainpage", app=mainpage_app)
app.mount(path="/personalspace", app=personalspace_app)


# 로그인 화면
@app.get("/")
async def index():
    return {"message": "Login Page"}

# 에러핸들러
# 404 에러핸들러
@app.exception_handler(404)
async def custom_404_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource could not be found."
        }
    )
# 422 에러핸들러
@app.exception_handler(422)
async def custom_422_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=422,
        content= {
            "error": "Unprocessable Entity",
            "message": "The request was well-formed but the server was unable to process the contained instructions.",
        }
    )


if(__name__ == "__main__"):
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)