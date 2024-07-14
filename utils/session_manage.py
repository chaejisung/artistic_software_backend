import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from pytz import timezone
import datetime

from utils.deps import get_session_coll

async def delete_expired_sessions(session_coll=get_session_coll()):
    now = datetime.now()
    await session_coll.delete({'expired_time': {'$lt': now}})

scheduler = AsyncIOScheduler()

async def session_manager(scheduler=scheduler):
    scheduler.add_job(
        delete_expired_sessions,
        CronTrigger(hour=12, minute=0, timezone=timezone('Asia/Seoul')),
        misfire_grace_time = 3600
        )
    
    scheduler.start()
    
async def scheduler_shutdown(scheduler=scheduler):
    scheduler.shutdown()
    