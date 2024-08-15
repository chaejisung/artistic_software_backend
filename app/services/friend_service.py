# libralies
from typing import Optional
from asyncio import create_task, gather
from fastapi.exceptions import HTTPException
from datetime import datetime, timezone, timedelta
# dto
from app.schemas.service_dto.friend_dto import (
    FriendApplyInput,
    FriendApplyOutput,
    FriendApplyResInput,
    FriendApplyResOutput,
    FriendSearchInput,
    FriendSearchOutput,
)
# 기타 사용자 모듈
from app.services.abs_service import AbsService
from app.deps import get_user_coll, get_friend_wait_coll, get_user_queue
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class FriendService(AbsService):
    instance: Optional["FriendService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "FriendService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance
    
    # 친구 신청
    @staticmethod
    async def friend_apply(input: FriendApplyInput,
                     user_coll: MongoDBHandler = get_user_coll(),
                     friend_wait_coll: MongoDBHandler = get_friend_wait_coll())->FriendApplyOutput:
        sender_id = input.sender_id
        receiver_id = input.receiver_id 
        # task 생성
        check_exist_user_task = create_task(user_coll.select({"_id": receiver_id}))
        check_is_requested_task = create_task(friend_wait_coll.select({"_id": {sender_id, receiver_id}}))
        
        # 본인 아이디로 친구 추가 혹은 존재하지 않는 아이디로 친구추가 -> 에러
        if(sender_id == receiver_id or await check_exist_user_task == False):
            raise HTTPException(status_code=400, detail="cannot send friend request")
        # 이미 친구인 유저에게 신청을 보낸 경우
        if(input.sender_friend_list is not None):
            if(receiver_id in input.sender_friend_list):
                return FriendApplyOutput(status = "already_friend")                    
        # 지금 대기중인 요청 혹은 이전에 거절된 요청으로부터 3일이 지나야 재신청, 아니면 에러
        # ttl 설정으로 3일 후에는 지워짐, 있으면 에러
        if(await check_is_requested_task != False):
            return FriendApplyOutput(status = "already_send")
        
        # 친구 요청 대기 컬렉션에 값 삽입
        friend_wait_data = {
            "_id": {"sender_id": sender_id, "receiver_id": receiver_id},
            "sender_id": sender_id,
            "receiver_id": receiver_id,
            "request_status": "pending",
            "request_date": datetime.now(timezone.utc)
        }
        
        await friend_wait_coll.insert(friend_wait_data)
        return FriendApplyOutput(status="success")
        
    # 친구 신청 응답(승낙 or 거절)
    @staticmethod
    async def friend_apply_response(input: FriendApplyResInput,
                                    user_coll: MongoDBHandler = get_user_coll(),
                                    friend_wait_coll: MongoDBHandler = get_friend_wait_coll())->FriendApplyOutput:
        sender_id = input.sender_id
        receiver_id = input.receiver_id
        
        # 친구 신청 대기 id
        composed_id = {"sender_id": sender_id, "receiver_id": receiver_id}
        
        # 있는지 없는지는 따로 확인 X(어차피 없으면 False 반환)
        if(input.consent_status): # 승낙
            friend_wait_process_result = await friend_wait_coll.delete({"_id": composed_id})
        else: # 거절
            friend_wait_process_result = await friend_wait_coll.update({"_id": composed_id}, {"$set": {"request_status": "denied"}})
        
        if(friend_wait_process_result == False):
            raise HTTPException(status_code=400, detail="Requested data does not exist")
        else:
            if(input.consent_status): # 승낙 + 각자 리스트에 삽입
                sender_friend_list_task = create_task(user_coll.update({"_id": sender_id}, {'$addToSet': {
                    "friend_list": receiver_id
                }}))
                receiver_friend_list_task = create_task(user_coll.update({"_id": receiver_id}, {'$addToSet': {
                    "friend_list": sender_id
                }}))
                await gather(sender_friend_list_task, receiver_friend_list_task)
                
                return FriendApplyResOutput(
                    consent_status=True,
                    sender_id=sender_id,
                    receiver_id=receiver_id
                )
            else: # 거절
                return FriendApplyResOutput(
                    consent_status=False,
                    sender_id=sender_id,
                    receiver_id=receiver_id
                )
    
    @staticmethod
    async def friend_search(input: FriendSearchInput,
                            user_coll: MongoDBHandler = get_user_coll())->FriendSearchOutput:
        search_word = input.search_word
        
        # 작업 생성 -> 이름검색, 태그 검색
        name_search_task = create_task(user_coll.select({"name": search_word}, {"_id": 1, "name": 1, "tag": 1}))
        tag_search_task = create_task(user_coll.select({"tag": search_word}, {"_id": 1, "name": 1, "tag": 1}))
        
        name_search_data = await name_search_task
        tag_search_data = await tag_search_task
        
        # 존재하지 않는 정보인 경우
        if(not(name_search_data or tag_search_data)):
            return FriendSearchOutput(exist_status=False)
        elif(name_search_data and not tag_search_data): # 이름 데이터만 존재
            return FriendSearchOutput(
                exist_status=True,
                user_data_list=name_search_data
            )
        elif(not name_search_data and tag_search_data): # 태그 데이터만 존재
            return FriendSearchOutput(
                exist_status=True,
                user_data_list=tag_search_data
            )
        else: # 모두 존재
            return FriendSearchOutput(
                exist_status=True,
                user_data_list=tag_search_data+name_search_data
            )
            
            

def get_friend_service():
    return FriendService.get_instance()