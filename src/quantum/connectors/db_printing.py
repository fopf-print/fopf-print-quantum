from uuid import UUID, uuid4

from quantum.core import db
from quantum.entities.printing import PrintingParameters, PrintingTask, PrintingTaskStatus


async def get_by_id(printing_task_id: UUID) -> PrintingTask:
    tasks = await db.fetchall(
        """
        select
             id
            ,file_id
            ,user_id
            ,message_id
            ,cost_cents
            ,status
            ,parameters
            ,created_dttm
            ,updated_dttm
        from
            printing_tasks
        where
            id = $1
        """,
        (printing_task_id,),
    )

    return PrintingTask.model_validate(tasks[0])


async def get_by_status(status: PrintingTaskStatus) -> list[PrintingTask]:
    tasks = await db.fetchall(
        """
        select
             id
            ,file_id
            ,user_id
            ,cost_cents
            ,status
            ,parameters
            ,created_dttm
            ,updated_dttm
        from
            printing_tasks
        where
            status = $1
        """,
        (status.value,),
    )

    return [PrintingTask.model_validate(t) for t in tasks]


async def set_task_status(printing_task_ids: list[UUID], new_status: PrintingTaskStatus):
    await db.execute(
        """
        update printing_tasks
        set
             status = $2
            ,updated_dttm = now() at time zone 'Europe/Moscow'
        where id = any($1)
        """,
        (printing_task_ids, new_status.value),
    )


async def create_printing_task(user_id: int, file_id: str, message_id: int) -> PrintingTask:
    task = await db.fetchall(
        '''
        insert into printing_tasks (id, file_id, user_id, message_id, cost_cents, status)
        values ($1, $2, $3, $4, $5, $6)
        returning
             id
            ,file_id
            ,user_id
            ,message_id
            ,cost_cents
            ,status
            ,parameters
            ,created_dttm
            ,updated_dttm
        ''',
        (uuid4(), file_id, user_id, message_id, -1, PrintingTaskStatus.cost_calculating),
    )

    print(task)
    print(task[0])
    return PrintingTask.model_validate(task[0])


async def set_printing_cost(printing_task_id: UUID, cost_cents: int):
    await db.execute(
        """
        update printing_tasks
        set
             cost_cents = $2
            ,updated_dttm = now() at time zone 'Europe/Moscow'
        where
            id = $1
        """,
        (printing_task_id, cost_cents),
    )


async def set_parameters(printing_task_id: UUID, parameters: PrintingParameters):
    await db.execute(
        """
        update printing_tasks
        set
             parameters = $2
            ,updated_dttm = now() at time zone 'Europe/Moscow'
        where
            id = $1
        """,
        (printing_task_id, parameters.model_dump_json()),
    )
