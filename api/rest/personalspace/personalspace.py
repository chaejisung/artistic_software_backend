import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Depends, Request, Response, APIRouter
from fastapi.responses import JSONResponse
from asyncio import create_task, gather

from api.middleware.session_middleware import SessionCheckMiddleware
from utils.deps import get_decor_coll,get_user_coll, get_user_space_coll, get_user_tasking_time_coll, get_decor_category
from utils.mongodb_handler import MongoDBHandler
from api.schema.schemas import RecordTime, TaskingNote, UpdateSpace

sub_app = FastAPI()
router = APIRouter()

# 미들웨어 추가
sub_app.add_middleware(SessionCheckMiddleware)

# 개인 공간에 필요한 정보 가져오기
@sub_app.get(path="/")
async def get_personalspace(request:Request,
                            user_coll:MongoDBHandler=Depends(get_user_coll),
                            user_space_coll:MongoDBHandler=Depends(get_user_space_coll),
                            user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)
                            ):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 본인 정보, 공간 정보, 집중 시간 정보 불러오기
    filter = {"_id": my_id}
    user_data_task = [
        create_task(user_coll.select(filter, limit=1)),
        create_task(user_space_coll.select(filter, limit=1)),
        create_task(user_tasking_time_coll.select(filter, limit=1))
    ]
    
    user_data_list = await gather(user_data_task)
    
    response_content = {
        "message": "All information has been successfully retrieved",
        "data": {
                "user_data": user_data_list[0],
                "user_space_data": user_data_list[1],
                "user_focustime_data": user_data_list[2],
                "length": {
                    "user_data_len": len(user_data_list[0]),
                    "user_space_data_len": len(user_data_list[1]),
                    "user_focustime_data_len": len(user_data_list[2])
                }
            },    
        }   
    
    return JSONResponse(content=response_content, status_code=200)

# 개인 공부 시간 기록 → 마칠 때 저장
@sub_app.post(path="/focustime/record")
async def get_focustime_record(request:Request,
                                 record_time:RecordTime,
                                 user_tasking_time_coll:MongoDBHandler=Depends(get_user_tasking_time_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 종료 시간 - 시작 시간 = 집중 시간
    focus_time = record_time.end_time - record_time.start_time

    # 전체 시간에 위 집중 시간 더하기
    total_time_task = create_task(user_tasking_time_coll.update({"_id", my_id}, {"$inc": {"today_tasking_time.total_time":focus_time}}))
    
    # 각 작업 종류에 값 넣기
    task_name = record_time.task_name
    filter_query = {
        "_id": my_id,
        f"today_tasking_time.task_specific_time.{task_name}": {"$exists": True}  # task_name이 존재하는 문서
    }
    update_query = {
        "$inc": {
            f"today_tasking_time.task_specific_time.$[elem].{task_name}": focus_time  # `task_name`의 값을 focus_time만큼 증가, 없으면 focus_time만큼 삽입
        }
    }
    specific_time_task = create_task(user_tasking_time_coll.update(filter=filter_query, update=update_query))

    await gather(total_time_task, specific_time_task)
    
    # 응답 컨텐츠 생성
    response_content = {
        "message": "Focus time Update Success",
        "data": {
            "task_name": task_name,
            "increase_focus_time": focus_time
        }
    }
    return JSONResponse(content=response_content, status_code=200)

# add, delete 모두 원래 taskingnote_Coll에도 값 넣어야함, 
# 이건 상욱이형이 다 짜고 난 후로 미루기
@sub_app.post(path="/taskingnote/add")
async def post_taskingnote_add(request:Request,
                               tasking_note:TaskingNote,
                               user_coll:MongoDBHandler=Depends(get_user_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    task_name = tasking_note.task_name
    
    # 유저 정보에 작업 데이터 삽입
    await user_coll.update({"_id":my_id}, {"$addToSet": {"tasks": task_name}})
    
    # 응답 컨텐츠 생성
    response_content = {
        "message": "Task Updated Successfully",
        "data": task_name
    }
    return JSONResponse(content=response_content, status_code=200)

# add, delete 모두 원래 taskingnote_Coll에도 값 넣어야함, 
# 이건 상욱이형이 다 짜고 난 후로 미루기
@sub_app.delete(path="/taskingnote/delete/{task_name}")
async def delete_taskingnote_delete(request:Request,
                               task_name:str,
                               user_coll:MongoDBHandler=Depends(get_user_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    # 유저 정보내 tasks 배열에서 삭제
    await user_coll.update({"_id": my_id}, {"$pull": {"tasks": task_name}})
    
    response_content = {
        "message": "Task Deleted Successfully",
        "data": task_name
    }
    return JSONResponse(content=response_content)

