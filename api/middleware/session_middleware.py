import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from starlette.middleware.sessions import SessionMiddleware as BaseSessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.exceptions import HTTPException
from asyncio import gather, create_task

from config.config import settings
from utils.deps import get_user_coll, get_session_coll

class SessionMiddleware(BaseSessionMiddleware):
    def __init__(self, app, secret_key: str):
        super().__init__(app, secret_key=secret_key, same_site="lax")
        
class SessionCheckMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.session_coll = get_session_coll()
        self.user_coll = get_user_coll()
    
    async def dispatch(self, request:Request, call_next):
        session_id = request.cookies.get("session_id")
        
        if(session_id):
            session_check = await self.session_coll.select(filter={"_id":session_id}, limit=1)

            if(not session_check):
                raise HTTPException(status_code=404)
            
            user_id = session_check[0]["identifier"]
            user_data = await self.user_coll.select(filter={"_id":user_id}, limit=1)
            if user_data:
                request.state.user = user_data[0]
            else:
                raise HTTPException(status_code=404)
            
        response = await call_next(request)
        return response
        

