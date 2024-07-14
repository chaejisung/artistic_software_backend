from typing import Dict
import asyncio

# 사용자별 큐 담는 딕셔너리
user_queues: Dict[int, asyncio.Queue] = {}