import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from fastapi import Request, HTTPException
from secrets import token_hex
from datetime import datetime, timedelta, timezone
from typing import Union

from api.schema.schemas import LoginUser
from utils.deps import get_user_coll, get_session_coll
from utils.mongodb_handler import MongoDBHandler


async def create_session(request: Request, user: LoginUser, 
                   user_coll:MongoDBHandler=get_user_coll(),
                   session_coll:MongoDBHandler=get_session_coll()) -> dict:
    user_id = user.id
    if(not await user_coll.select({"_id": user_id}, limit=1)):
        user_coll_data = {
            "_id": user_id,
            "name": user.name,
            "email": user.email
        }
        await user_coll.insert(user_coll_data)
    
    current_time = datetime.now(timezone.utc)
    expire_time = current_time + timedelta(hours=2, minutes=30)
    
    session_id = token_hex(16)
    
    session_coll_data = {
        "_id": session_id,
        "identifier": user_id, # 이건 user_coll의 _id 참조하게끔
        "created_time": current_time,
        "expired_time": expire_time
    }
    print("세션콜렉션데이터", session_coll_data)
    
    await session_coll.insert(session_coll_data)
    
    return {
            "key":"session_id",
            "value":session_id,
            "expires":expire_time,
            "httponly":True,
            "secure":True,
            "samesite":'Lax'
        }
    
    
    

def get_current_user(request: Request) -> LoginUser:
    user_data = request.session.get('user')
    if not user_data:
        raise HTTPException(status_code=401, detail="Failed")
    return LoginUser(**user_data)
