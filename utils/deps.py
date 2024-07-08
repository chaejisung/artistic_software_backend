import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from utils.mongodb_handler import MongoDBHandler

# MongoDB 핸들러 인스턴스(의존성)-유저데이터, 데스크장식물데이터
def get_user_coll() -> MongoDBHandler:
    return MongoDBHandler(coll_config={"coll_name": "user_coll"})

def get_user_space_coll() -> MongoDBHandler:
    return MongoDBHandler(coll_config={"coll_name": "user_space_coll"})

def get_user_tasking_time_coll() -> MongoDBHandler:
    return MongoDBHandler(coll_config={"coll_name": "user_tasking_time_coll"})

def get_decor_coll() -> MongoDBHandler:
    return MongoDBHandler(coll_config={"coll_name": "decor_coll"})

def get_session_coll() -> MongoDBHandler:
    return MongoDBHandler(coll_config={"coll_name": "session_coll"})

def get_decor_category()->list:
    return ['desk', 'lamp', 'monitor', 'vase', 'bookshelf', 'frame'] # 현재는 이정도