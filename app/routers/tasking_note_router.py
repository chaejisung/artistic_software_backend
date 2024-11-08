#libraries
from fastapi import APIRouter, Depends, Request, Response
# 미들웨어
from app.middleware.session.session_middleware import SessionMiddleware
# 의존성 
from app.services.tasking_note_service import TaskingNoteService, get_taskingnote_service
# DTO 
# 요청
from app.schemas.request_dto.taskingnote_request import (
    CreateBookReq,
    UpdateBookReq,
    DeleteBookReq,
    WritePageReq,
)
# 응답
from app.schemas.response_dto.taskingnote_response import (
    CreateBookRes,
    UpdateBookRes,
    WritePageRes,
    GetPageTextRes,
    GetPageImageRes,
    GetPageFileRes,
    OpenBookRes,
    GetBookListRes
)
# 프로세스
from app.schemas.service_dto.tasking_note_dto import (
    CreateNoteInputDto, CreateNoteOutputDto,
    UpdateNoteInputDto, UpdateNoteOutputDto,
    DeleteNoteInputDto,
    WritePageInputDto, WritePageOutputDto,
    GetTextInputDto, GetTextOutputDto,
    GetImageInputDto, GetImageOutputDto,
    GetFileInputDto, GetFileOutputDto,
    OpenBookInputDto, OpenBookOutputDto
)

router = APIRouter()

@router.post("/create",
             summary="책을 만드는 api",
             description="세션 필요, 책 제목과 간단한 책 설명 적으면 생성")
async def create_book(request: Request,
                      response: Response,
                      input: CreateBookReq,
                      taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> CreateBookRes:
    user_data = await SessionMiddleware.session_check(request)
    if(user_data == False):
        response.status_code = 404
        return response
    
    user_id = user_data.get("_id")
    note_title = input.note_title
    note_description = input.note_description
    note_color = input.note_color

    create_note_input = CreateNoteInputDto(
        user_id=user_id,
        note_title=note_title,
        note_description=note_description,
        note_color=note_color
    )
    create_note_output: CreateNoteOutputDto = await taskingnote_service.create_note(create_note_input)
    print("크리에이트", create_note_output)

    if(create_note_output is None):
        response.status_code = 204
        return response

    return CreateBookRes(
        user_id=create_note_output.user_id,
        note_title=create_note_output.note_title,
        note_description=create_note_output.note_description,
        note_color=create_note_output.note_color
    )

@router.put("/update",
             summary="책 이름이랑 설명 수정하는 api",
             description="세션 필요, 책 이름, 설명 수정함, 설명 수정 안하고 싶으면 note_description에 \"\"(빈 문자열) 넣어서 보내기 ")
async def update_book(request: Request,
                      input: UpdateBookReq,
                      taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    note_title = input.note_title
    new_note_title = input.new_note_title
    new_note_description = input.new_note_description
    new_note_color = input.new_note_color

    update_note_input = UpdateNoteInputDto(
        user_id=user_id,
        note_title=note_title,
        new_note_title=new_note_title,
        new_note_description=new_note_description,
        new_note_color=new_note_color
    )

    update_note_output: UpdateNoteOutputDto = await taskingnote_service.update_note(update_note_input)

    return UpdateBookRes(
        user_id=update_note_output.user_id,
        note_title=update_note_output.note_title,
        note_description=update_note_output.note_description,
        note_color=update_note_output.note_color
    )

@router.delete("/delete",
             summary="책을 삭제하는 api",
             description="세션 필요, 책 제목 보내면 삭제함")
async def delete_book(request: Request,
                      response: Response,
                      input: DeleteBookReq,
                      taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request)

    user_id = user_data.get("_id")
    note_title = input.note_title

    delete_note_input = DeleteNoteInputDto(
        user_id = user_id,
        note_title = note_title
    )
    await taskingnote_service.delete_note(delete_note_input)

    response.status_code = 204
    return response 

@router.get("/open/{book_title}",
             summary="책을 열람하는 api",
             description="""세션 필요, 경로 파라미터로 책 제목을 보내면 열람 가능 
            만일 한 장도 적혀있지 않은 책이면 204 응답,
            그게 아니면 1페이지 내용 응답(총 페이지 수도 응답)
             """)
async def oepn_book(request: Request,
                    response: Response,
                    book_title: str,
                    taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request) 

    user_id = user_data.get("_id")

    open_book_input = OpenBookInputDto(
        user_id=user_id,
        note_title=book_title
    )

    open_book_output: OpenBookOutputDto = taskingnote_service.open_book(open_book_input)

    if(open_book_output is None):
        response.status_code = 204
        return response

    return OpenBookRes(
        user_id = open_book_output.user_id,
        note_title = open_book_output.note_title,
        note_description= open_book_output.note_description,
        page_count=open_book_output.page_count,
        page_text=open_book_output.page_text
    )


    
@router.post("/page/write",
             summary="책에 내용을 쓰는 api",
             description="""세션 필요, 책 제목 필요
             text, image, file을 보낼 것
             image, file은 {1: 이미지 or 파일} 처럼 몇 번째인지 : 이미지 or 파일 형태로 보낼 것
             """)
async def write_page(request: Request,
                     response: Response,
                      input: WritePageReq,
                      taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> WritePageRes:
    user_data = await SessionMiddleware.session_check(request)    

    user_id = user_data.get("_id")
    note_title = input.note_title
    note_page = input.note_page

    write_page_input = WritePageInputDto(
        user_id=user_id,
        note_title=note_title,
        note_page=note_page,
        note_text=input.note_text,
        note_image=input.note_image,
        note_file=input.note_file   
    )

    write_page_output: WritePageOutputDto = await taskingnote_service.write_page(write_page_input)

    if(write_page_output is None):
        response.status_code = 204
        return response
    
    return WritePageRes(
        user_id=write_page_output.user_id,
        note_title=write_page_output.note_title,
        note_page=write_page_output.note_page
    )

@router.get("/page/text",
             summary="특정 페이지의 글자를 가져오는 api",
             description="세션 필요, 글자만 가져오는 api")
async def get_page_text(request: Request,
                        note_title: str,
                        note_page: str,
                        taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request)    

    user_id = user_data.get("_id")

    get_text_input = GetTextInputDto(
        user_id=user_id,
        note_title=note_title,
        note_page=note_page
    )

    get_text_output: GetTextOutputDto = await taskingnote_service.get_text(get_text_input)

    return GetPageTextRes(
        note_title=get_text_output.note_title,
        note_page=get_text_output.note_page,
        page_text=get_text_output.page_text
    )

@router.get("/page/image",
             summary="특정 페이지의 이미지를 가져오는 api",
             description="세션 필요, 이미지만 가져오는 api")
async def get_page_image(request: Request,
                        note_title: str,
                        note_page: str,
                        taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request)    

    user_id = user_data.get("_id")

    get_image_input = GetImageInputDto(
        user_id-user_id,
        note_title=note_title,
        note_page=note_page
    )

    get_image_output: GetImageOutputDto = await taskingnote_service.get_image(get_image_input)

    return GetPageImageRes(
        note_title=get_image_output.note_title,
        note_page=get_image_output.note_page,
        page_image=get_image_output.page_image
    )

@router.get("/page/file",
             summary="특정 페이지의 파일을 가져오는 api",
             description="세션 필요, 파일만 가져오는 api")
async def get_page_file(request: Request,
                        note_title: str,
                        note_page: str,
                        taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)) -> UpdateBookRes:
    user_data = await SessionMiddleware.session_check(request)    

    user_id = user_data.get("_id")

    get_file_input = GetFileInputDto(
        user_id-user_id,
        note_title=note_title,
        note_page=note_page
    )

    get_file_output: GetFileOutputDto = await taskingnote_service.get_image(get_file_input)

    return GetPageFileRes(
        note_title=get_file_output.note_title,
        note_page=get_file_output.note_page,
        page_image=get_file_output.page_file
    )

@router.get("/list", summary="책 목록 불러오기, 세션id 필요")
async def get_book_list(request: Request,
                        taskingnote_service: TaskingNoteService = Depends(get_taskingnote_service)):
    user_data = await SessionMiddleware.session_check(request)    

    user_id = user_data.get("_id")

    book_list = await taskingnote_service.get_book_list(user_id)

    return GetBookListRes(book_list=book_list)




