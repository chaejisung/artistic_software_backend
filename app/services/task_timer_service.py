from app.deps import get_user_tasking_time_coll, MongoDBHandler
from app.schemas.response_dto.task_timer_response import TaskTimerResponse
from fastapi import Depends
from typing import Optional

class TaskTimerService:
    instance: Optional["TaskTimerService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "TaskTimerService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance

    # 타이머 시간 저장
    @staticmethod
    async def save_task_timer(user_id: str, time_in_seconds: int,
                              task_time_coll: MongoDBHandler = get_user_tasking_time_coll()) -> TaskTimerResponse:
        await task_time_coll.update(
            {"_id": user_id},
            {"$set": {"today_tasking_time": time_in_seconds}}
        )
        return TaskTimerResponse(message="타이머 시간 저장 성공", time_in_seconds=time_in_seconds)

    # 타이머 시간 불러오기
    @staticmethod
    async def get_task_timer(user_id: str, task_time_coll: MongoDBHandler = get_user_tasking_time_coll()) -> TaskTimerResponse:
        user_timer = await task_time_coll.select({"_id": user_id})
        if user_timer:
            return TaskTimerResponse(message="타이머 시간 불러오기 성공", time_in_seconds=user_timer.get("today_tasking_time", 0))
        else:
            return TaskTimerResponse(message="타이머 기록이 없습니다.", time_in_seconds=0)

    # 타이머 리셋
    @staticmethod
    async def reset_task_timer(user_id: str, task_time_coll: MongoDBHandler = get_user_tasking_time_coll()) -> TaskTimerResponse:
        await task_time_coll.update(
            {"_id": user_id},
            {"$set": {"today_tasking_time": 0}}
        )
        return TaskTimerResponse(message="타이머 리셋", time_in_seconds=0)
    
def get_task_timer_service():
    return TaskTimerService.get_instance()    
