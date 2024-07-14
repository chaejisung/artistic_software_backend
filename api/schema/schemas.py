from pydantic import BaseModel
from datetime import datetime


class LoginUser(BaseModel):
    id: str
    email: str
    name: str

class RecordTime(BaseModel):
    task_name: str
    start_time: datetime
    end_time: datetime
    
class TaskingNote(BaseModel):
    task_name:str
    task_etc:dict
    
class UpdateSpace(BaseModel):
    id: str
    space: list
    
class AddFriendUser(BaseModel):
    id: str
    
class ResponseFriendReq(BaseModel):
    user_id: str
    accept_status: bool