from uuid import uuid4

from quantum.core import db
from quantum.entities.printing import PrintingTaskStatus


async def create_printing_task(user_id: int, message_id: int, file_id: str):
    await db.execute(
        '''
        insert into printing_tasks (id, user_id, message_id, file_id, status)
        values ($1, $2, $3, $4)
        ''',
        [
            uuid4(), user_id, message_id, file_id, PrintingTaskStatus.new.value
        ]
    )
