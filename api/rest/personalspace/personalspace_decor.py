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

from api.rest.personalspace.personalspace import sub_app, router

# 이건 세션 인증 필요 없으므로 성능상 이유로 라우터로 분리
# 꾸미기 요소 카탈로그 보여주기
@router.get(path="/decor/catalog")
async def get_decor_catalog(decor_category:list=Depends(get_decor_category),
                            decor_coll:MongoDBHandler=Depends(get_decor_coll)):
    # 전체 요소 한번에 가져오기
    task_func = lambda x: decor_coll.select({"decor_category": x})
    decor_task_list = map(task_func, decor_category)
    decor_data = await gather(decor_task_list)
    
    # 응답 컨텐츠 생성
    response_content = {
        "message":"All information has been successfully retrieved"
    }
    for i in range(len(decor_category)):
        response_content.update({decor_category[i]: decor_data[i]})
        
    return JSONResponse(content=response_content, status_code=200)

# 공간 꾸민 후 정보 보내기, 아직 user_spcae_coll이 미정이라 update_space 나중에 바꿔야함
@sub_app.put(path="/decor/space")
async def put_decor_space(request:Request,
                        update_space:UpdateSpace,
                        user_space_coll:MongoDBHandler=Depends(get_user_space_coll)):
    # 미들웨어에서 넘겨받은 유저 데이터
    my_data = request.state.user
    my_id = my_data.get("_id")
    
    update_space_data = update_space.model_dump
    await user_space_coll.update({"_id": my_id}, {'$set': update_space_data})
    
    response_content = {
        "message": "Space Update Success"
    }
    return JSONResponse(content=response_content)