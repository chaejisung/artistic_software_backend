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