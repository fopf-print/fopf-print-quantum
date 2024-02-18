from quantum.entities.printing import PrintingTask
from quantum.connectors import mb_printing_queue


def test_push_then_pop_task():
    task = PrintingTask(
        user_id=1,
        message_id=123,
        printer_id=0,
        policy={
            'lisis_per_page': 'two_lists_per_page',
            'n_sides_printing': 'both_sides_printing'
        }
    )

    assert mb_printing_queue.insert_task(task) == True
    assert mb_printing_queue.try_get_task() == task
