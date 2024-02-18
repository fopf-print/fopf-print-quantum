#  Когда-нибудь тут будет взаимодействие с RabbitMQ при помощи
# библиотеки pika.
#  Потанцевально это будет полезно, если одновременно запущенных воркеров
# будет больше чем 1. В этом случае хранить очередь локально больше не
# получится.
#
#  До тех самых пор наша очередь - это `list`)

from collections import deque
from quantum.entities.printing import PrintingTask

# Ну а вот и сама очередь
_queue: deque[PrintingTask] = deque()


def insert_task(task: PrintingTask) -> bool:
    _queue.appendleft(task)
    return True


def try_get_task() -> PrintingTask | None:
    if len(_queue):
        return _queue.pop()
    return None
