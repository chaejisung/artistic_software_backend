import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import FastAPI, Depends, Request, Response
from fastapi.responses import JSONResponse

from api.middleware.session_middleware import SessionCheckMiddleware
from utils.deps import get_decor_coll,get_user_coll, get_user_space_coll, get_user_tasking_time_coll
from utils.mongodb_handler import MongoDBHandler
from asyncio import create_task, gather

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

