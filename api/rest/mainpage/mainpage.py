import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.exceptions import HTTPException
from asyncio import create_task, gather, Queue
from typing import Dict

from config.config import settings
from utils.deps import get_user_coll, get_user_tasking_time_coll, get_user_space_coll, get_friend_wait_coll
from api.middleware.session_middleware import SessionCheckMiddleware
from api.schema.schemas import AddFriendUser
from utils.mongodb_handler import MongoDBHandler
from utils.server_sent_event import user_queues

sub_app = FastAPI()

# 미들웨어 추가
sub_app.add_middleware(SessionCheckMiddleware)

# 본인+친구들 정보 불러오기
@sub_app.get(path="/")
async def get_mainpage(request:Request, 
                       user_coll:MongoDBHandler=Depends(get_user_coll), 
                       user_space_coll:MongoDBHandler=Depends(get_user_space_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    # 유저 데이터 받아오기
    my_space = create_task(user_space_coll.select({"_id": my_id}, limit=1))
    
    # 유저 데이터 바탕으로 친구 데이터 받아오기
    friend_id = my_data.get("friend_id")
    if(friend_id is not None):
        friend_data_list = [create_task(user_coll.select({"_id": id}, limit=1)) for id in friend_id]
        friend_space_list = [create_task(user_space_coll.select({"_id": id}, limit=1)) for id in friend_id]
    
        friend_data= await gather(*friend_data_list)
        friend_space = await gather(*friend_space_list)
    
    my_space = await my_space
    
    # 응답 설명 메시지 설정
    if(friend_id is None):
        response_message = "There is only personal data with no friend data"
    else:
        response_message = "Personal and friend data have been transmitted."
    
    # 유저들의 정보
    response_content = {
        "message": response_message,
        "data": {
            "user_data": {
                "my_data": my_data,
                "friend_data": friend_data
            },
            "user_space_data":{
                "my_space_data": my_space,
                "friend_space_data": friend_space
                },
            "length":{
                "my_data_len": len(my_data),
                "my_space_data_len": len(my_space),
                "friend_data_len": len(friend_data),
                "friend_space_data_len": len(friend_data)
            }
        }
    }
    
    return JSONResponse(content=response_content, status_code=200)

# 작업 시간 가져오기
@sub_app.get(path="/focustime")
async def get_mainpage_focustime(request:Request, 
                                user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    friend_id = my_data.get("friend_id")
    
    # 사용자 집중 시간 가져오기
    my_focustime = create_task[user_tasking_time_coll.select({"_id":my_id}, {"today_tasking_time"}, 1)]
    
    if(friend_id is None):
        response_message = "There is only personal data with no friend data"
    else:
        response_message = "Personal and friend data have been transmitted."
        
    friend_focus_time_list = [create_task(user_tasking_time_coll.select({"_id": id}, {"today_tasking_time":1}, 1)) for id in friend_id]
    
    # 응답 데이터 구성
    response_content = {
        "message": response_message,
        "data": {
            "my_focustime_data": await my_focustime,
            "friend_focustime_list": await friend_focus_time_list,
            "length": {
                "my_focustime_data": len(await my_focustime),
                "friend_focustime_list": len(await friend_focus_time_list)
                
            }
        }
    }
    
    return JSONResponse(content=response_content, status_code=200)

# 사용자 정보+공간 불러오기 -> 인증 필요
@sub_app.get(path="/user/{user_id}")
async def get_mainpage_studytime(request:Request, 
                                 user_id:str,
                                 user_coll:MongoDBHandler=Depends(get_user_coll),
                                 user_space_coll:MongoDBHandler=Depends(get_user_space_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    friend_id = my_data.get("friend_id")
    
    # 친구 데이터 존재 시 불러오는 작업
    if(friend_id is not None):
        friend_data = create_task(user_coll.select({"_id": user_id}, limit=1))
        user_space = create_task(user_space_coll.select({"_id": user_id}, limit=1))
    
        # 본인 또는 친구가 아닌 경우 오류
        if(user_id != my_id or user_id not in friend_id):
            raise HTTPException(status_code=422)
        
        # 본인 데이터거나 친구 데이터일 때 정보 불러오기
        if(user_id == my_id):
            user_data = my_data
        else:
            user_data = await friend_data
    
        user_space_data = await user_space
        
        
        response_content = {
            "message": "Requested Data Successfully Found and Returned",
            "data": {
                "user_data": user_data,
                "user_space_data": user_space_data[0],
                "length": {
                    "user_data_len": len(user_data),
                    "user_space_data_len": len(user_space_data)
                    }
                }
        }
    else:
        if(user_id != my_id):
            raise HTTPException(status_code=422)
        else:
            user_data = my_data
            
        response_content = {
            "message": "Requested Data Successfully Found and Returned",
            "data": {
                "user_data": user_data,
                "user_space_data": [],
                "length": {
                    "user_data_len": len(user_data),
                    "user_space_data_len": 0
                    },
                },
            
        }
    
    return JSONResponse(content=response_content, status_code=200)
    
# 친구 활동 중 확인 -> 이건 어캐하지


# 친구 요청, 전체 공지, 메모장 보내는 SSE 엔드포인트
@sub_app.get("/sse")
async def get_mainpage_sse(request:Request,
                           user_queues=user_queues):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    async def get_events(user_queues = user_queues):
        while True:
            queue_data = await user_queues[my_id].get()
            if(queue_data is None):
                break
            yield queue_data
    
    async def close_queue():
        await request.is_disconnected()
        await user_queues[my_id].put(None)
        
    create_task(close_queue())
    
    return StreamingResponse(get_events(), media_type="text/event-stream")