from pydantic import BaseModel, Field
from typing import Optional, Union, Tuple, Dict, List
from bson import ObjectId
from datetime import datetime

class DecorColl(BaseModel):
    _id: Optional[str] = Field(default_factory=ObjectId, alias='_id')
    decor_category: str
    decor_size: Tuple[float, float, float]
    decor_image: Union[bytes, str]
    decor_cost: int
    decor_etc: Optional[Dict[str, str]]
    
    class Config:
        allow_population_by_field_name = True  # alias를 사용한 필드명으로도 데이터 생성 가능
        
class SessionColl(BaseModel):
    _id: Optional[str] = Field(default_factory=ObjectId, alias='_id')
    identifier: str # 참조 키(->UserColl), 이건 추후 구현
    created_time: datetime
    expired_time: datetime
    
    class Config:
        allow_population_by_field_name = True  # alias를 사용한 필드명으로도 데이터 생성 가능

class UserColl(BaseModel):
    _id: Optional[str] = Field(default_factory=ObjectId, alias='_id')
    name: str
    email: str
    phone_number: str
    email: str
    age: int
    frined_id: List[str]
    tasks: List[str]
   
    class Config:
        allow_population_by_field_name = True  # alias를 사용한 필드명으로도 데이터 생성 가능

class UserSpaceColl(BaseModel):
    _id: Optional[str] = Field(default_factory=ObjectId, alias='_id')
    # _id가 UserColl 참조
    
    # 아직 미정
    space: List[str]
    
    class Config:
        allow_population_by_field_name = True  # alias를 사용한 필드명으로도 데이터 생성 가능

class TaskingTimeType(BaseModel):
    total_time: datetime
    task_specifit_time: List[Dict[str, str]]

class UserTaskingTimeColl(BaseModel):
    _id: Optional[str] = Field(default_factory=ObjectId, alias='_id')
    # _id가 UserColl 참조
    
    today_tasking_time: TaskingTimeType
    previous_tasking_time: List[TaskingTimeType]
    
    class Config:
        allow_population_by_field_name = True  # alias를 사용한 필드명으로도 데이터 생성 가능
