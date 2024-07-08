import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from motor.motor_asyncio import AsyncIOMotorClient
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
        
        print(f"{coll_name} collection is connected")
    
    #close connection - Async
    def close(self):
        if(MongoDBHandler.db_conn is not None):
            MongoDBHandler.db_conn.close()
    
    #CRUD - insert, select, update, delete
    # insert - Async
    async def insert(self, documents:Union[dict, list], session=None)->int:
        try:
            if(type(documents) is dict):
                result = await self.db_coll.insert_one(documents, session=session)
                print("insert 1 items")
                return 1
            elif(type(documents) is list):
                # 이거 insert_one을 여러번 해서 오류처리도 가능,
                # insert_many랑 성능 비교해서 추후에 수정
                result = await self.db_coll.insert_many(documents, session=session)
            
                print(f"insert {len(result.inserted_ids)} items")
                return len(result.inserted_ids)
        
        except Exception as e:
            print("Insert Method Error: ",e)
            return -1
    
    # select - Async
    async def select(self, filter:dict={}, projection:dict=None, limit:int=0):
        try:
            if(limit == 1):
                result = await self.db_coll.find_one(filter, projection)
                result_list = [result] if result else []
                result_len = len(result_list)
                print(f"find 1 documents")
                return result_list
            else:
                cursor = self.db_coll.find(filter, projection)
                if(limit > 0):
                    cursor = cursor.limit(limit)
                
                result_list = await cursor.to_list(None)
                    
                await cursor.close()
                
                result_len = len(result_list)
                print(f"find {result_len} documents")
                return result_list
                
            
            
            
        except Exception as e:
            print("Selet Method Error: ", e)
            return [-1]
        
    # update - Async
    async def update(self, filter:dict={}, update:dict=None, limit:int=0, session=None)->int:
        try:
            if(limit == 1):
                result = await self.db_coll.update_one(filter, update, session=session)
            else:
                result = await self.db_coll.update_many(filter, update, session=session)
            
            print(f"update {result.modified_count} documents")
            return result.modified_count
        except Exception as e:
            print("Update Method Error: ",e)
            return -1
    
    # delete - Async
    async def delete(self, filter:dict={}, limit:int=0, session=None)->int:
        try:
            if(limit == 1):
                result = await self.db_coll.delete_one(filter, session=session)
            else:
                result = await self.db_coll.delete_many(filter, session=session)

            print(f"delete {result.deleted_count} documents")
            return result.deleted_count
        except Exception as e:
            print("Delete Method Error: ",e)
            return -1
        
    async def start_transaction(self, tasks):
        async with await MongoDBHandler.db_conn.start_session() as session:
            async with session.start_transaction():
                try:
                    await tasks(session)
                    
                    await session.commit_transaction()
                    print("Transaction committed")
                    return True
                except:
                    await session.abort_transaction()
                    print("Transaction aborted")
                    return False
    