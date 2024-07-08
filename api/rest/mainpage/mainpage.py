import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Request, Depends
from fastapi.responses import JSONResponse
from fastapi.exceptions import HTTPException
from asyncio import create_task, gather

from config.config import settings
from utils.deps import get_user_coll, get_user_tasking_time_coll, get_user_space_coll
from api.middleware.session_middleware import SessionCheckMiddleware
from utils.mongodb_handler import MongoDBHandler

sub_app = FastAPI()

# 미들웨어 추가
sub_app.add_middleware(SessionCheckMiddleware)

# 본인+친구들 정보 불러오기
@sub_app.get(path="/")
async def get_mainpage(request:Request, 
                       user_coll:MongoDBHandler=Depends(get_user_coll), 
                       user_space_coll:MongoDBHandler=Depends(get_user_space_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    my_space = create_task(user_space_coll.select({"_id": my_id}, limit=1))
    
    friends_data_list = []
    friends_space_list = []
    
    friends_id = my_data.get("friend_id")
    if(friends_id is not None):
        friends_data_list = [create_task(user_coll.select({"_id": id}, limit=1)) for id in friends_id]
        friends_space_list = [create_task(user_space_coll.select({"_id": id}, limit=1)) for id in friends_id]
    
        friends_data_list = await gather(*friends_data_list)
        friends_space_list = await gather(*friends_space_list)
    
    my_space = await my_space
    
    user_data = [my_data, *friends_data_list]
    user_space_data = [*my_space, *friends_space_list]
    
    response_content = {
        "data": {
            "user_data": user_data,
            "user_space_data": user_space_data
                 },
        "length": {
            "user_data": len(user_data),
            "user_space_data": len(user_space_data)
                 },
    }
    
    return JSONResponse(content=response_content)

# 친구 추가 -> 이거 추가하려는 친구가 없으면 rollback해야하는데 그건 나중에
@sub_app.get(path="/friend/add/{user_id}")
async def get_mainpage_friend_add(request: Request,
                                  user_id:str,
                                  user_coll:MongoDBHandler=Depends(get_user_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 내 아이디 == 추가하려는 아이디 or 추가하려는 id가 존재하지 않으면 오류
    if(my_id == user_id or await user_coll.select({"_id":my_id}, {"_id"}, limit=1) == []):
        raise HTTPException(status_code=400)
    # 이미 있으면 끝
    if(user_id in my_data["friend_id"]):
        response_content = {
            "message": "This friend is already added."
        }
        return JSONResponse(content=response_content)
    
    task1 = create_task(user_coll.update({"_id":user_id},{"$pull":{"friend_id":my_id}}))
    task2 = create_task(user_coll.update({"_id":my_id},{"$pull":{"friend_id":user_id}}))
    
    response_content = {
        "data": [my_id, user_id]
    }
    
    await gather(task1, task2)
    
    return JSONResponse(content=response_content)

# 친구 삭제
@sub_app.get(path="/friend/delete/{user_id}")
async def get_friend_delete(request: Request, 
                            user_id:str,
                            user_coll:MongoDBHandler=Depends(get_user_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 내 아이디 == 삭제하려는 아이디면 오류
    if(my_id == user_id):
        raise HTTPException(status_code=400)
    # 원래 없으면 끝
    if(user_id not in my_data["friend_id"]):
        response_content = {
            "message": "The friend no longer exists."
        }
        return JSONResponse(content=response_content)
    
    task1 = create_task(user_coll.update({"_id":user_id},{"$push":{"friend_id":my_id}}))
    task2 = create_task(user_coll.update({"_id":my_id},{"$push":{"friend_id":user_id}}))
    
    response_content = {
        "data": [my_id, user_id]
    }
    
    await gather(task1, task2)
    
    return JSONResponse(content=response_content)

# 작업 시간 가져오기
@sub_app.get(path="/taskingtime")
async def get_mainpage_taskingtime(request:Request, 
                                user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    my_tasking_time = create_task[user_tasking_time_coll.select({"_id":my_id}, {"today_tasking_time"}, 1)]
    
    friends_id = my_data["friend_id"]
    friends_tasking_list = [create_task(user_tasking_time_coll.select({"_id": id}, {"today_tasking_time":1}, 1)) for id in friends_id]
    
    response_content = {
        "data": [await my_tasking_time] + await friends_tasking_list,
        "length": [1, len(await friends_tasking_list)]
    }
    
    return JSONResponse(content=response_content)

# 사용자 정보+공간 불러오기 -> 인증 필요
@sub_app.get(path="/user/{user_id}")
async def get_mainpage_studytime(request:Request, 
                                 user_id:str,
                                user_coll:MongoDBHandler=Depends(get_user_coll),
                                user_space_coll:MongoDBHandler=Depends(get_user_space_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    friends_id = my_data.get("friend_id")
    
    if(friends_id is not None):
        friend_data = create_task(user_coll.select({"_id": user_id}, limit=1))
        user_space = create_task(user_space_coll.select({"_id": user_id}, limit=1))
    
    # 본인 또는 친구가 아닌 경우 오류
        if(user_id != my_id or user_id not in friends_id):
            raise HTTPException(status_code=400)
        if(user_id == my_id):
            user_data = my_data
        else:
            user_data = await friend_data
    
        user_space_data = await user_space
        response_content = {
            "data": {
                "user_data": user_data,
                "user_space_data": user_space_data[0]
                    },
            "length": {
                "user_data": len(user_data),
                "user_space_data": len(user_space_data)
                    },
        }
    else:
        if(user_id != my_id):
            raise HTTPException(status_code=400)
        else:
            user_data = my_data
            
        response_content = {
            "data": {
                "user_data": user_data,
                "user_space_data": []
                    },
            "length": {
                "user_data": len(user_data),
                "user_space_data": 0
                    },
        }
    
    return JSONResponse(content=response_content)
    
# 친구 활동 중 확인 -> 이건 어캐하지
