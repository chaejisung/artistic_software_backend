import os, sys, dotenv
dotenv.load_dotenv()
sys.path.append(os.getenv("BACKEND_PATH"))

from datetime import datetime
import asyncio

from utils.deps import get_decor_coll, get_user_coll, get_user_space_coll, get_user_tasking_time_coll

decor_coll_data = [
    {
        "_id": "wood desk",
        "decor_category": "desk",
        "decor_size": (24.0, 36.0, 1.5),
        "decor_image": "base64encodedstring1",
        "decor_cost": 120,
        "decor_etc": {"artist": "John Doe", "material": "canvas"}
    },
    {
        "_id": "stone desk",
        "decor_category": "desk",
        "decor_size": (10.0, 10.0, 30.0),
        "decor_image": "base64encodedstring2",
        "decor_cost": 300,
        "decor_etc": {"artist": "Jane Smith", "material": "marble"}
    },
    {
        "_id": "blue vase",
        "decor_category": "vase",
        "decor_size": (8.0, 8.0, 15.0),
        "decor_image": "base64encodedstring3",
        "decor_cost": 80,
        "decor_etc": {"artist": "Emily Brown", "material": "ceramic"}
    }
]

user_coll_data = [
    {
        "_id": "user_1",
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "phone_number": "123-456-7890",
        "age": 30,
        "frined_id": ["friend1", "friend2"],
        "tasks": ["task1", "task2"]
    },
    {
        "_id": "user_2",
        "name": "Bob Williams",
        "email": "bob@example.com",
        "phone_number": "987-654-3210",
        "age": 25,
        "frined_id": ["friend3", "friend4"],
        "tasks": ["task3", "task4"]
    },
    {
        "_id": "user_3",
        "name": "Charlie Brown",
        "email": "charlie@example.com",
        "phone_number": "555-555-5555",
        "age": 28,
        "frined_id": ["friend5", "friend6"],
        "tasks": ["task5", "task6"]
    }
]

user_space_coll_data = [
    {
        "_id": "user_1",
        "space": ["space1", "space2"]
    },
    {
        "_id": "user_2",
        "space": ["space3", "space4"]
    },
    {
        "_id": "user_3",
        "space": ["space5", "space6"]
    }
]

user_tasking_time_coll_data = [
    {
        "_id": "user_1",
        "today_tasking_time": {
            "total_time": datetime(2024, 7, 7, 2, 30, 0),
            "task_specifit_time": [
                {"task1": "1 hour"},
                {"task2": "1.5 hours"}
            ]
        },
        "previous_tasking_time": [
            {
                "total_time": datetime(2024, 7, 6, 2, 0, 0),
                "task_specifit_time": [
                    {"task1": "1 hour"},
                    {"task2": "1 hour"}
                ]
            }
        ]
    },
    {
        "_id": "user_2",
        "today_tasking_time": {
            "total_time": datetime(2024, 7, 7, 3, 0, 0),
            "task_specifit_time": [
                {"task3": "2 hours"},
                {"task4": "1 hour"}
            ]
        },
        "previous_tasking_time": [
            {
                "total_time": datetime(2024, 7, 6, 1, 30, 0),
                "task_specifit_time": [
                    {"task3": "0.5 hour"},
                    {"task4": "1 hour"}
                ]
            }
        ]
    },
    {
        "_id": "user_3",
        "today_tasking_time": {
            "total_time": datetime(2024, 7, 7, 1, 45, 0),
            "task_specifit_time": [
                {"task5": "1 hour"},
                {"task6": "0.75 hour"}
            ]
        },
        "previous_tasking_time": [
            {
                "total_time": datetime(2024, 7, 6, 2, 15, 0),
                "task_specifit_time": [
                    {"task5": "1 hour"},
                    {"task6": "1.25 hours"}
                ]
            }
        ]
    }
]

dc = get_decor_coll()
uc = get_user_coll()
usc = get_user_space_coll()
uttc = get_user_tasking_time_coll()

async def set_db():
    await dc.insert(decor_coll_data)
    await uc.insert(user_coll_data)
    await usc.insert(user_space_coll_data)
    await uttc.insert(user_tasking_time_coll_data)

asyncio.run(set_db())
