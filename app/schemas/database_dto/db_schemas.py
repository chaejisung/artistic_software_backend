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
    """
    id: str = Field(default_factory=str, alias="_id")
    name: str
    email: str
    tag: str
    accessibility: bool = True
    friend_list: Optional[List[str]] = None
    show_profile: bool = False

# 세션 정보 컬렉션+캐시
class SessionColl(BaseModel):
    """
    1. 랜덤 생성 유저 id
    2. 유저 소셜로그인 식별자
    3. 세션 유지 시간(ttl)
    4. 엑세스 토큰
    """
    id: str = Field(default_factory=str, alias="_id")
    identifier: str
    created_at: Union[datetime, str]
    access_token: Optional[str]

# 사용자 집중 시간 컬렉션   => 이 부분 수정
class TaskingTime(BaseModel):
    total_time: int = 0
    task_specific_time: Dict[str, int] = {}# 작업 : 시간 -> 30분, 150분
    
class UserTaskingTimeColl(BaseModel):
    id: str = Field(default_factory=str, alias="_id")
    today_tasking_time: int = 0
    previous_tasking_time: Dict[str, int] = {} # 날짜: 그 날 시간
 
# 친구 추가 요청 대기 컬렉션  ㅌ
class FriendWaitColl(BaseModel):
    id: Dict[str, str] = Field(..., alias="_id") # {내 아이디, 친구아이디}
    sender_id: str
    receiver_id: str
    request_status: Literal["pending", "denied"]
    request_date: Union[datetime, str]

# 개인 공간 정보
class FurnitureArrange(BaseModel):
    decor_id: str
    location: List[float]

class BoardInfo(BaseModel):
    sender_id: str
    sender_name: str
    content: str
    date: datetime # 이거 나중에 ttl 설정으로 삭제하게
    

class UserSpaceColl(BaseModel):
    """
    1. userid와 동일
    2. interior_data => 공간의 인테리어 데이터 
    3. memo_list => 메모 남기기 -> 단순 문자열
    4. board => 친구들이 게시물 적는 공간
    5. music_url => 음악 리스트 담는 공간
    6. light_color => 빛 색상
    7. book_list => 책 이름 리스트 -> [(책제목, 번호)]
    """
    id: str = Field(default_factory=str, alias="_id")
    interior_data: List[Union[FurnitureArrange, List]] = []
    memo_list: List[List[Union[str, List[int]]]] = []
    board: Optional[List[BoardInfo]] = None 
    music_url: Optional[List[str]] = None
    light_color: Literal[0, 1, 2, 3] = 0
    book_list: List[List[Union[str, Literal[0,1,2,3]]]] = []

# 장식품 정보 저장 컬렉션
class DecorColl(BaseModel):
    decor_id: str = Field(default_factory=str, alias="_id")
    decor_category: Literal["desk", "chair", "shelf", "lamp", "clock", "computer", "etc"]
    decor_size: Tuple[float, float, float]
    decor_cost: int
    decor_etc: dict


# 책 내부 내용 정보 저장 -> 이거 변동 있으므로 스키마 러프하게 잡기
# id는 user_id와 동일하지 않음
class TaskingNoteColl(BaseModel):
    """
    1. _id -> 몽고id -> 자동
    2. user_id -> 소유자 id
    2. note_title => user_coll에서 들고 있음
    3. note_description => 안써도 됨
    4. note_color -> 책 색상
    5. page_count -> 총 페이지 수
    6. text -> {페이지: 내용}
    7. image -> {{image파일} : 내용}
    8. file -> {{파일} : 내용}
    """
    user_id:str 
    note_title: str
    note_description: Optional[str] = ""
    note_color: Literal[0,1,2,3]
    page_count: int = 0
    text: dict = {} ## 텍스트, 이미지, 파일 모두 리스트+인덱스 조합이 맞는 듯 싶음
    image: dict = {}
    file: dict = {}
    