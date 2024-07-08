import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse
from asyncio import create_task, gather

from api.middleware.session_middleware import SessionCheckMiddleware
from utils.deps import get_decor_coll,get_user_coll, get_user_space_coll, get_user_tasking_time_coll
from utils.mongodb_handler import MongoDBHandler
from api.schema.schemas import RecordTime, TaskingNote

sub_app = FastAPI()

# 미들웨어 추가
sub_app.add_middleware(SessionCheckMiddleware)

@sub_app.get()
async def get_personalspace(request:Request,
                            user_coll:MongoDBHandler=Depends(get_user_coll),
                            user_space_coll:MongoDBHandler=Depends(get_user_space_coll),
                            user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)
                            ):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    filter = {"_id": my_id}
    user_data_task = [
        create_task(user_coll.select(filter, limit=1)),
        create_task(user_space_coll.select(filter, limit=1)),
        create_task(user_tasking_time_coll.select(filter, limit=1))
    ]
    
    user_data_list = await gather(user_data_task)
    response_content={
        "data": {
            "user_data": user_data_list[0],
            "user_space_data": user_data_list[1],
            "user_tasking_time_data": user_data_list[2]
                 },
        "length": {
            "user_data": len(user_data_list[0]),
            "user_space_data": len(user_data_list[1]),
            "user_tasking_time_data": len(user_data_list[2])
        }
    }
    
    return JSONResponse(content=response_content)

# 개인 공부 시간 기록 → 마칠 때 저장
@sub_app.post(path="/taskingtime/record")
async def get_taskingtime_record(request:Request,
                                 record_time:RecordTime,
                                 user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 일단 today_tasking_time을 전체로 보기
    focus_time = record_time.end_time - record_time.start_time

    total_time_task = create_task(user_tasking_time_coll.update({"_id", my_id}, {"$inc": {"today_tasking_time.total_time":focus_time}}))
    
    task_name = record_time.task_name
    filter_query = {
        "_id": my_id,
        f"today_tasking_time.task_specific_time.{task_name}": {"$exists": True}  # task_name이 존재하는 문서
    }
    update_query = {
        "$inc": {
            f"today_tasking_time.task_specific_time.$[elem].{task_name}": focus_time  # `task_name`의 값을 focus_time만큼 증가, 없므녀 focus_time만큼 삽입
        }
    }
    
    specific_time_task = create_task(user_tasking_time_coll.update(filter=filter_query, update=update_query))

    await gather(total_time_task, specific_time_task)
    response_content = {
        "message": "Time Update Success"
    }
    return JSONResponse(content=response_content)

# add, delete 모두 원래 taskingnote_Coll에도 값 넣어야함, 
# 이건 상욱이형이 다 짜고 난 후로 미루기
@sub_app.post(path="/taskingnote/add")
async def post_taskingnote_add(request:Request,
                               tasking_note:TaskingNote,
                               user_coll:MongoDBHandler=Depends(get_user_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    task_name = tasking_note.task_name
    
    await user_coll.update({"_id":my_id}, {"$addToSet": {"tasks": task_name}})
    
    response_content = {
        "message": "Task Update Success"
    }
    return JSONResponse(content=response_content)
    
@sub_app.delete(path="/taskingnote/delete/{task_name}")
async def delete_taskingnote_delete(request:Request,
                               task_name:str,
                               user_coll:MongoDBHandler=Depends(get_user_coll)):
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    await user_coll.update({"_id": my_id}, {"$pull": {"tasks": task_name}})
    
    response_content = {
        "message": "Task Delete Success"
    }
    return JSONResponse(content=response_content)

