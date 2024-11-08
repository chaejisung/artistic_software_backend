from pydantic import BaseModel

class UpdateUserNameRequest(BaseModel):
    user_id: str
    new_name: str

class UpdateUserProfileReq(BaseModel):
    profile_status: bool