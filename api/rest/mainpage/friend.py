import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from asyncio import create_task, gather
import datetime

from config.config import settings
from utils.deps import get_user_coll, get_user_tasking_time_coll, get_user_space_coll, get_friend_wait_coll
from api.middleware.session_middleware import SessionCheckMiddleware
from api.schema.schemas import AddFriendUser, ResponseFriendReq
from utils.mongodb_handler import MongoDBHandler
from utils.server_sent_event import user_queues

from api.rest.mainpage.mainpage import sub_app

# 친구 추가 -> 이거 추가하려는 친구가 없으면 rollback해야하는데 그건 나중에
@sub_app.post(path="/friend/add")
async def post_mainpage_friend_add(request: Request,
                                  friend_user: AddFriendUser,
                                  user_queues =user_queues,
                                  user_coll: MongoDBHandler=Depends(get_user_coll),
                                  friend_wait_coll: MongoDBHandler=Depends(get_friend_wait_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    user_id = friend_user.id
    
    # 내 아이디 == 추가하려는 아이디 or 추가하려는 id가 존재하지 않으면 오류
    if(my_id == user_id or not (await user_coll.select({"_id":my_id}, {"_id"}, limit=1)["task_status"])):
        raise HTTPException(status_code=422)
    
    # 이미 있으면 이미 존재한다고 메시지만 반환
    if(user_id in my_data["friend_id"]):
        response_content = {
            "message": "This friend is already added."
        }
        return JSONResponse(content=response_content, status_code=204)
    
    composite_id = {"my_id": my_id, "friend_id": user_id}
    check_friend_wait = await friend_wait_coll.select({"_id": composite_id})
    
    # 이전 거절된 요청 or 대기중 요청으로부터 일주일이 지나야 재 신청가능
    if(datetime.now() - check_friend_wait["data"]["request_date"] > datetime.timedelta(weeks=1)):
        await friend_wait_coll.delete({"_id": composite_id})
    
    # 친구요청 대기 컬렉션에 값 삽입
    friend_wait_data = {
        "_id": composite_id,
        "requester_id": my_id,
        "receiver_id": user_id,
        "request_status": "pending",
        "request_date": datetime.now()
    }
    friend_wait_task = create_task(friend_wait_coll.insert(friend_wait_data))
    
    # /mainpage/sse로 보낼 정보
    queue_message = {
        "source": request.url.path,
        "data": {
            "requester_id": my_id,
            "receiver_id": user_id
        }
    }
    
    # 일주일 내로 이미 요청을 보낸 경우
    if(await friend_wait_task == -1): 
        response_content = {
            "message": "Already sent a request."
        }
        return JSONResponse(content=response_content, status_code=204)
    # 조건이 모두 성립하면 비동기 큐에 데이터 넣기
    else: 
        await user_queues[user_id].put(queue_message)
    
    
    # 정상적으로 친구요청이 완료된 경우의 응답
    response_content = {
            "message": "Request has been successfully sent",
            "data": {
                "requester_id": my_id,
                "receiver_id": user_id
            }
        }
    
    return JSONResponse(content=response_content, status_code=200)

# 친구 신청 응답(수락, 거절)
@sub_app.post(path="/friend/response")
async def post_mainpage_friend_response(request: Request,
                                        response_friend_req: ResponseFriendReq,
                                        friend_wait_coll: MongoDBHandler=Depends(get_friend_wait_coll),
                                        user_coll: MongoDBHandler=Depends(get_user_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    user_id = response_friend_req.user_id
    accept_status = response_friend_req.accept_status
    
    composite_id = {"my_id": my_id, "friend_id": user_id}
    # 거절 당하면 -> 문서 상태 reject로 변경
    if(accept_status == False):
        task = create_task(friend_wait_coll.update({"_id": composite_id}, {'$set': {'request_status': 'reject'}}, limit=1))
        response_message =  "Request Rejected"
        await task
    
    # 수락하면 -> 문서에서 삭제, 친구 리스트에 추가
    else:
        friend_wait_coll_task = create_task(friend_wait_coll.delete({"_id": composite_id}))
        my_coll_task = create_task(user_coll.update({"_id": my_id}, {'$push': {"friend_id": user_id}}))
        friend_coll_task = create_task(user_coll.update({"_id": user_id}, {'$push': {"friend_id": my_id}}))
        response_message = "Request Accepted"
        await gather(friend_wait_coll_task, my_coll_task, friend_coll_task)
        
    response_content = {
        "message": response_message,
        "data": {
                "requester_id": user_id,
                "receiver_id": my_id
            }
    }
        
    return JSONResponse(content=response_content, status_code=200)


# 친구 삭제
@sub_app.delete(path="/friend/delete/{user_id}")
async def delete_mainpage_friend_delete(request: Request, 
                                        user_id:str,
                                        user_coll:MongoDBHandler=Depends(get_user_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 내 아이디 == 삭제하려는 아이디면 오류
    if(my_id == user_id):
        raise HTTPException(status_code=422)
    # 원래 없으면 끝
    if(user_id not in my_data["friend_id"]):
        response_content = {
            "message": "The friend no longer exists."
        }
        return JSONResponse(content=response_content, status_code=204)
    
    # DB에서 삭제하는 작업
    task1 = create_task(user_coll.update({"_id":user_id},{"$pull":{"friend_id":my_id}}))
    task2 = create_task(user_coll.update({"_id":my_id},{"$pull":{"friend_id":user_id}}))
    
    response_content = {
        "message": "Friend removed successfully.",
        "data": {
            "my_id": my_id,
            "friend_id": user_id
            }
        }
    
    await gather(task1, task2)
    
    return JSONResponse(content=response_content, status_code=200)