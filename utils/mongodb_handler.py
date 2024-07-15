import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from motor.motor_asyncio import AsyncIOMotorClient
from asyncio import create_task, gather
from typing import Union, Any

from config.config import Settings, settings


class MongoDBHandler():
    db_conn = None
    
    ## initialize and connect - Sync
    def __init__(self, mongodb_config:Settings=settings, coll_config:dict=None)->Any:
        self.host = mongodb_config.MONGODB_HOST
        self.port = mongodb_config.MONGODB_PORT
        self.user = mongodb_config.MONGODB_USER
        self.password = mongodb_config.MONGODB_PASSWORD
        self.db_coll = None
        
        if(MongoDBHandler.db_conn is None):
            try:
                MongoDBHandler.db_conn = AsyncIOMotorClient(host=self.host, port=self.port)
            except Exception as e:
                print(e)
        
        
        if(coll_config is not None):
            db_name = mongodb_config.MONGODB_DB_NAME
            coll_name = coll_config["coll_name"]
        try:
            if(db_name is not None and coll_name is not None):
                self.db_coll = MongoDBHandler.db_conn[db_name][coll_name]
            else:
                raise("Please enter the database name and collection name")
        except Exception as e:
            print(e)
        
        print(f"MONGODB: {coll_name} collection is connected")
    
    #close connection - Async
    def close(self):
        if(MongoDBHandler.db_conn is not None):
            MongoDBHandler.db_conn.close()
    
    #CRUD - insert, select, update, delete
    # insert - Async
    async def insert(self, documents:Union[dict, list], session=None)->dict:
        try:
            if(type(documents) is dict):
                result = await self.db_coll.insert_one(documents, session=session)
                return {
                    "task_status": result.acknowledged,
                    "data": result.inserted_id
                }
            elif(type(documents) is list):
                # batch_size(현재는 100) 기준으로 작업 분할
                insert_tasks = []
                batch_size = 100
                while (len(documents) >= batch_size):
                    insert_tasks.append(create_task(self.db_coll.insert_many(documents[0: batch_size], session=session)))
                    del documents[0: batch_size]
                if(len(documents) != 0):
                    insert_tasks.append(create_task(self.db_coll.insert_many(documents, session=session)))
                    
                # 분할된 작업 결과 바탕으로 결과 생성, 성능차이 없으므로 for문 사용
                task_result = await insert_tasks
                inserted_ids = []
                acknowledge = True
                for divided_result in task_result:
                    inserted_ids.extend(divided_result.inserted_ids)
                    acknowledge = acknowledge and divided_result.acknowledged
                
                return {
                    "task_status": acknowledge,
                    "data": inserted_ids
                }

        except Exception as e:
            print("Insert Method Error: ",e)
            return {
                "task_status": False
            }
    
    # select - Async
    async def select(self, filter:dict={}, projection:dict=None, limit:int=0):
        try:
            if(limit == 1):
                result = await self.db_coll.find_one(filter, projection)
                # 만일 없으면 오류 발생
                if(result is None):
                    print("Cannot find data from collection.")
                    raise
                
                return {
                    "task_status": True,
                    "data": result
                }
            else:
                cursor = self.db_coll.find(filter, projection)
                if(limit > 0):
                    cursor = cursor.limit(limit)
                # 데이터 없으면 오류 발생
                if (cursor.count_documents({}) == 0):
                    print("Cannot find data from collection.")
                    raise
                
                # 결과 생성
                result_list = await cursor.to_list(None)
                await cursor.close()
                return {
                    "task_status": True,
                    "data": result_list
                }
            
        except Exception as e:
            print("Selet Method Error: ", e)
            return { 
                "task_status": False
            }
        
    # update - Async
    async def update(self, filter:dict={}, update:dict=None, limit:int=0, session=None)->int:
        try:
            if(limit == 1):
                result = await self.db_coll.update_one(filter, update, session=session)
            else:
                result = await self.db_coll.update_many(filter, update, session=session)
            
            return {
                "task_status": result.acknowledged,
                "data": result.modified_count
            } 
                
            
        except Exception as e:
            print("Update Method Error: ",e)
            return { 
                "task_status": False
            }
    
    # delete - Async
    async def delete(self, filter:dict={}, limit:int=0, session=None)->int:
        try:
            if(limit == 1):
                result = await self.db_coll.delete_one(filter, session=session)
            else:
                result = await self.db_coll.delete_many(filter, session=session)

            # 분할된 작업 결과 바탕으로 결과 생성, 성능차이 없으므로 for문 사용
            
            return {
                "task_status": result.acknowledged,
                "data": result.deleted_count
            } 
        
        except Exception as e:
            print("Delete Method Error: ",e)
            return { 
                "task_status": False
            }
    
    # # 트랜젝션 만든거, 실제로는 못쓰고 있음
    # async def start_transaction(self, tasks):
    #     async with await MongoDBHandler.db_conn.start_session() as session:
    #         async with session.start_transaction():
    #             try:
    #                 await tasks(session)
                    
    #                 await session.commit_transaction()
    #                 print("Transaction committed")
    #                 return True
    #             except:
    #                 await session.abort_transaction()
    #                 print("Transaction aborted")
    #                 return False
    