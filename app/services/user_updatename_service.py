from app.utils.db_handlers.mongodb_handler import MongoDBHandler
from app.schemas.request_dto.user_updatename_request import UpdateUserNameRequest
from app.deps import get_user_coll
from typing import Optional


class UserService:
    instance: Optional["UserService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "UserService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance

    @staticmethod
    async def update_user_name(user_id: str, new_name: str,
                               user_coll: MongoDBHandler = get_user_coll()) -> bool:
        try:
            
            # 이름 업데이트
            update_result = await user_coll.update(
                {"_id": user_id},
                {"$set": {"name": new_name}}
            )
            
            # 업데이트 성공여부 반환
            return update_result != 0
        except Exception as e:
            print(f"UserService Update Error: {e}")
            return False

    @staticmethod
    async def update_profile(user_id: str, profile_url: bool,
                             user_coll: MongoDBHandler = get_user_coll()):
        update_result = await user_coll.update(
            {"_id": user_id},
            {"$set": {"show_profile": profile_url}}
        )

        return update_result != 0



def get_user_service():
    return UserService.get_instance()