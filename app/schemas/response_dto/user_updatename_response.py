from pydantic import BaseModel

class UpdateUserNameResponse(BaseModel):
  message: str
  user_id: str
  new_name: str
  

class UpdateProfileRes(BaseModel):
  profile_status: bool