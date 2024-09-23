from pydantic import BaseModel, Field
from typing import Optional, Union, Literal, Tuple, Dict, List
from bson import ObjectId
from datetime import datetime

# 사용자 정보 컬렉션
class UserColl(BaseModel):
    """
    1. 유저 id(소셜로그인 식별자)
    2. 유저 이름
    3. 유저 이메일
    4. 유저 태그(친추용)
    5. 접근 가능
    
    6. 친구 리스트 -> 필수X
    7. 작업 -> 필수X
    """
    id: str = Field(default_factory=str, alias="_id")
    name: str
    email: str
    tag: str
    accessibility: bool = False
    
    friend_list: Optional[List[str]] = None
    tasks: Optional[List[str]] = None

# 세션 정보 컬렉션+캐시
class SessionColl(BaseModel):
    """
    1. 랜덤 생성 유저 id
    2. 유저 소셜로그인 식별자
    3. 세션 유지 시간(ttl)
    """
    id: str = Field(default_factory=str, alias="_id")
    identifier: str
    created_at: Union[datetime, str]

# 사용자 집중 시간 컬렉션   
class TaskingTime(BaseModel):
    total_time: int
    task_specific_time: Dict[str, int] # 작업 : 시간 -> 30분, 150분
    
class UserTaskingTimeColl(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    today_tasking_time: TaskingTime
    previous_tasking_time: Dict[Union[str,datetime], TaskingTime] # 날짜: 그 날 시간
 
# 친구 추가 요청 대기 컬렉션  
class FriendWaitColl(BaseModel):
    id: Dict[str, str] = Field(..., alias="_id") # {내 아이디, 친구아이디}
    sender_id: str
    receiver_id: str
    request_status: Literal["pending", "denied"]
    request_date: Union[datetime, str]

# 개인 공간 정보
class FurnitureArrange(BaseModel):
    decor_id: str
    location: Tuple[float, float, float]

class BoardInfo(BaseModel):
    sender_id: str
    sender_name: str
    content: str
    date: datetime # 이거 나중에 ttl 설정으로 삭제하게
    

class UserSpaceColl(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    interior_data: List[FurnitureArrange]
    todo_list: List[str] = []
    board: Optional[List[BoardInfo]] = None 
    music_url: Optional[List[str]] = None
    light_color: Literal[0, 1, 2, 3] = 0

# 장식품 정보 저장 컬렉션
class DecorColl(BaseModel):
    decor_id: str = Field(default_factory=str, alias="_id")
    decor_category: Literal["desk", "chair", "shelf", "lamp", "clock", "computer", "etc"]
    decor_size: Tuple[float, float, float]
    decor_cost: int
    decor_etc: dict
    

    
    