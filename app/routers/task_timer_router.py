from fastapi import APIRouter, Depends, Request
from app.schemas.response_dto.task_timer_response import TaskTimerResponse
from app.services.task_timer_service import TaskTimerService, get_task_timer_service
from app.middleware.session.session_middleware import SessionMiddleware
from pydantic import BaseModel

router = APIRouter()

class TimeInSec(BaseModel):
    time_in_seconds: int

# 타이머 시간 저장
@router.post("/task-timer/save", response_model=TaskTimerResponse)
async def save_timer(
    request: Request,
    time_in_seconds: TimeInSec,
    task_timer_service: TaskTimerService = Depends(get_task_timer_service),
):
    
    time_in_seconds = time_in_seconds.time_in_seconds
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")

    result = await task_timer_service.save_task_timer(user_id, time_in_seconds)
    return result

# 타이머 시간 불러오기
@router.get("/task-timer", response_model=TaskTimerResponse)
async def get_timer(
    request: Request,
    task_timer_service: TaskTimerService = Depends(get_task_timer_service),
):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")

    result = await task_timer_service.get_task_timer(user_id)
    return result

# 타이머 리셋
@router.post("/task-timer/reset", response_model=TaskTimerResponse)
async def reset_timer(
    request: Request,
    task_timer_service: TaskTimerService = Depends(get_task_timer_service),
):
    user_data = await SessionMiddleware.session_check(request)
    user_id = user_data.get("_id")

    result = await task_timer_service.reset_task_timer(user_id)
    return result
