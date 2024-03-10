from quantum.connectors import db_printing


async def create_printing_task(user_id: int, message_id: int, file_id: str):
    await db_printing.create_printing_task(user_id, message_id, file_id)
