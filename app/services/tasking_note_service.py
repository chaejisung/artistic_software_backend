# libralies
from typing import Optional
from asyncio import create_task, gather, sleep
# dto
from app.schemas.service_dto.tasking_note_dto import (
    CreateNoteInputDto, CreateNoteOutputDto,
    UpdateNoteInputDto, UpdateNoteOutputDto,
    DeleteNoteInputDto,
    WritePageInputDto, WritePageOutputDto,
    OpenBookInputDto, OpenBookOutputDto,
    GetTextInputDto, GetTextOutputDto,
    GetImageInputDto, GetImageOutputDto,
    GetFileInputDto, GetFileOutputDto,
    DeletePageInput,
)
# 기타 사용자 모듈
from app.configs.config import settings
from app.services.abs_service import AbsService
from app.deps import get_user_coll, get_taskingnote_coll, get_user_space_coll
from app.utils.db_handlers.mongodb_handler import MongoDBHandler

class TaskingNoteService(AbsService):
    instance: Optional["TaskingNoteService"] = None
    # 싱글톤 반환
    @classmethod
    def get_instance(cls) -> "TaskingNoteService":
        if(cls.instance is None):
            cls.instance = cls()
        return cls.instance

    # 책 -> 책 생성, 책 수정(이름), 책 삭제 / 책은 소유자id, 책 이름으로 식별
    # 책 생성 -> id는 유저아이디, 이름, 설명만 받고 그대로 반환
    @staticmethod
    async def create_note(input: CreateNoteInputDto,
                          user_space_coll: MongoDBHandler = get_user_space_coll(),
                          taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> CreateNoteOutputDto:
        book_list = await user_space_coll.select({"_id": input.user_id})
        book_list = book_list.get("book_list")

        # print("book_list_len", len(book_list))
        # if(len(book_list) >= 8):
        #     return None
        print("book_list   ", book_list)
        for item in book_list:
            if item[0] == input.note_title:
                return None

        # tasking note(책) 생성
        note_dict = {
            "user_id": input.user_id,
            "note_title": input.note_title,
            "note_description": input.note_description,
            "note_color": input.note_color
        }
        note_task = create_task(taskingnote_coll.insert(note_dict))

        # user space에 넣기
        space_task = create_task(user_space_coll.update(
            {"_id": input.user_id},
            {
                "$push": {
                    "book_list": (input.note_title, input.note_color)
                }
            }
        ))

        await gather(note_task, space_task)
        
        return CreateNoteOutputDto(
            user_id = input.user_id,
            note_title=input.note_title,
            note_description=input.note_description,
            note_color=input.note_color
        )
    
    # 책 수정 -> id는 유저아이디, 이름, 설명만 받고 그대로 반환
    @staticmethod
    async def update_note(input: UpdateNoteInputDto,
                          user_space_coll: MongoDBHandler = get_user_space_coll(),
                          taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> UpdateNoteOutputDto:        
        # task 생성(user_space_coll, taskingnote_coll 모두)
        # 유저 리스트에서 변경
        user_space_book_list = (await user_space_coll.select(
            {"_id": input.user_id},
            {"book_list": 1}
        )).get("book_list")
        # userSpace에 값 수정
        for i in range(len(user_space_book_list)):
            if(user_space_book_list[i][0] == input.note_title):
                if(input.new_note_title is not None):
                    user_space_book_list[i][0] = input.new_note_title
                if(input.new_note_color is not None):
                    user_space_book_list[i][1] = input.new_note_color
                break
        # 업데이트 하는 태스크
        user_space_update_task = create_task(
            user_space_coll.update(
                {"_id": input.user_id},
                {
                    "$set": {"book_list": user_space_book_list}
                }
            )
        )
        # 있는 값만 수정하게 내부 쿼리 세팅
        set_inner_query = {}
        if(input.new_note_title is not None):
            set_inner_query["note_title"] = input.new_note_title
        if(input.new_note_description is not None):
            set_inner_query["note_description"] = input.new_note_description
        if(input.new_note_color is not None):
            set_inner_query["note_color"] = input.new_note_color
        # taskingnote에 수정하는 테스크
        taskingnote_update_task = create_task(taskingnote_coll.update(
            {"user_id": input.user_id, "note_title": input.note_title}, {"$set" : set_inner_query}
        ))
        # 비동기 작업 대기
        await gather(user_space_update_task, taskingnote_update_task)

        return UpdateNoteOutputDto(
            user_id=input.user_id,
            note_title=input.new_note_title,
            note_description=input.new_note_description,
            note_color=input.new_note_color
        )

    # 책 삭제 -> id는 유저아이디, 이름만 받음 반환X
    @staticmethod
    async def delete_note(input: DeleteNoteInputDto,
                          user_space_coll: MongoDBHandler = get_user_space_coll(),
                          taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> None:
        # 테스크 생성
        user_space_delete_task = create_task(
            user_space_coll.update(
                {"_id": input.user_id},
                {"$pull": {"book_list": {"$elemMatch": {"0": input.note_title}}}}
            )
        )
        taskingnote_delete_task = create_task(taskingnote_coll.delete({"user_id": input.user_id, "note_title": input.note_title}))
        # 테스크 완료
        await gather(user_space_delete_task, taskingnote_delete_task)
        return 

    # 페이지 -> 페이지 생성, 페이지 삭제, 페이지 조회(조회는 파일, 이미지, 텍스트 분리), 텍스트만 수정
    # 페이지 생성 및 수정 -> 맞는 책이 없으면 None 반환
    @staticmethod ## 이거 수정 필요
    async def write_page(input: WritePageInputDto,
                         taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> WritePageOutputDto:
        user_id = input.user_id
        note_title = input.note_title
        note_page = input.note_page

        # 테스크 생성
        text_update_task = create_task(taskingnote_coll.update(
            {"user_id": user_id, "note_title": note_title}, 
            {"$set": {f"text.{note_page}": input.note_text}
        }))
        image_update_task = create_task(sleep(0)) # 없는 경우 대비
        file_update_task = create_task(sleep(0)) # 없는 경우 대비
  
        # 이미지 or 파일이 있는 경우의 태스크 생성 {{file: 책이름_페이지_번호}}
        if(input.note_image is not None): 
            processed_image = {}
            for key, value in input.note_image.items():
                new_key = str({{"image: "+note_title+"_"+str(note_page)+"_"+key}})
                processed_image[new_key] = value
            image_update_task = create_task(taskingnote_coll.update(
                {"user_id": user_id, "note_title": note_title}, 
                {"$set": {f"image.{note_page}": processed_image}}
            ))
        if(input.note_file is not None):
            processed_file = {}
            for key, value in input.note_file.items():
                new_key = str({{"file: "+note_title+"_"+str(note_page)+"_"+key}})
                processed_file[new_key] = value
            file_update_task = create_task(taskingnote_coll.update(
                {"user_id": user_id, "note_title": note_title}, 
                {"$set": {f"file.{note_page}": input.note_file}}
            ))
        # 태스크 실행
        (t1, t2, t3) = await gather(text_update_task, image_update_task, file_update_task)
        await taskingnote_coll.update({"user_id": user_id, "note_title": note_title},
                                      {'$inc': {'page_count': 1}})
        # updated_count = t1+t2+t3

        # if(updated_count == 0):
        #     return None

        return WritePageOutputDto(
            user_id=input.user_id,
            note_title = input.note_title,
            note_page=input.note_page
        )
    
    @staticmethod
    async def open_book(input: OpenBookInputDto,
                       taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> OpenBookOutputDto:
        user_id = input.user_id
        note_title = input.note_title

        note_data = await taskingnote_coll.select({"user_id": user_id, "note_title": note_title}, 
                                                  {"note_title": 1, "note_description": 1, "page_count": 1, "text": 1})
        
        if(note_data.get("page_count") <= 0):
            return None

        return OpenBookOutputDto(
            user_id=note_data.get("user_id"),
            note_title=note_data.get("note_title"),
            note_description=note_data.get("note_description"),
            page_count=note_data.get("page_count"),
            page_text=note_data.get("page_text")
        )


    # 페이지 조회(텍스트) -> input으로 소유자id, note_title, page 받기
    @staticmethod
    async def get_text(input: GetTextInputDto,
                       taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> GetTextOutputDto:
        user_id = input.user_id,
        note_title = input.note_title
        note_page = input.note_page

        total_text = await taskingnote_coll.select({"user_id": user_id, "note_title": note_title}, {"text": 1})
        page_text = total_text.get(str(note_page))
        
        return GetTextOutputDto(
            user_id=user_id,
            note_title=note_title,
            note_page=note_page,
            page_text=page_text
        )
    
    # 페이지 조회(이미지) -> input으로 소유자id, note_title, page 받기
    @staticmethod
    async def get_image(input: GetImageInputDto,
                       taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> GetImageOutputDto:
        user_id = input.user_id,
        note_title = input.note_title
        note_page = input.note_page 

        total_image = await taskingnote_coll.select({"user_id": user_id, "note_title": note_title}, {"image": 1})
        page_image = total_image.get(str(note_page))


        return GetImageOutputDto(
            user_id=user_id,
            note_title=note_title,
            note_page=note_page,
            page_image=page_image
        )

    # 페이지 조회(파일) -> input으로 소유자id, note_title, page 받기
    @staticmethod
    async def get_file(input: GetFileInputDto,
                       taskingnote_coll: MongoDBHandler = get_taskingnote_coll()) -> GetFileOutputDto:
        user_id = input.user_id
        note_title = input.note_title
        note_page = input.note_page 

        total_file = await taskingnote_coll.select({"user_id": user_id, "note_title": note_title}, {"file": 1})
        page_file = total_file.get(str(note_page))

        return GetFileOutputDto(
            user_id=user_id,
            note_title=note_title,
            note_page=note_page,
            page_file=page_file
        )
    
    # 페이지 삭제 -> 소유자id, note_title, page받기 -> count도 하나 줄이기
    @staticmethod
    async def delete_page(input: DeletePageInput,
                          taskingnote_coll: MongoDBHandler = get_taskingnote_coll()):
        user_id = input.user_id
        note_title = input.note_title
        note_page = str(input.note_page)

        page_count_check = await taskingnote_coll.select({"user_id": user_id, "note_title": note_title}, {"page_count":1})

        if(page_count_check > 0 and page_count_check <= note_page):
            page_decrease_task = create_task(taskingnote_coll.update({"user_id": user_id, "note_title": note_title}, {"$inc": {"page_count": -1}}))
            page_text_task = create_task(taskingnote_coll.update({"user_id": user_id, "note_title": note_title}, {"$unset": {f"text.{note_page}": ""}}))
            page_image_task = create_task(taskingnote_coll.update({"user_id": user_id, "note_title": note_title}, {"$unset": {f"image.{note_page}": ""}}))
            page_file_task = create_task(taskingnote_coll.update({"user_id": user_id, "note_title": note_title}, {"$unset": {f"file.{note_page}": ""}}))

            await gather(page_decrease_task, page_text_task, page_image_task, page_file_task)
        else:
            return None
        
    @staticmethod
    async def get_book_list(user_id: str,
                            user_space_coll: MongoDBHandler = get_user_space_coll()):
        book_list = (await user_space_coll.select({"_id": user_id}, {"book_list": 1})).get("book_list")
        return book_list

def get_taskingnote_service():
    return TaskingNoteService.get_instance()