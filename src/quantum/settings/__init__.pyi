# при импорте settings модуль заменяется на класс
# но хочется иметь подсказки и нематерящийся mypy

# поэтому поля классов Settings перечислены тут


yookassa_shop_id: str
"""идентификатор магазина yookassa"""

yookassa_api_key: str
"""ключ магазина yookassa"""

redirect_after_payment_url: str
"""урл для редиректа после оплаты"""

postgres_connection_uri: str
"""строка для подключения к pg"""

fopf_print_bot_token: str
"""токен для основного тг-бота"""

filestorage_path: str
"""путь до файлопомойки для временного хранения pdf-файлов"""

refill_worker_delay_sec: int
"""пауза в работе воркера пополнения"""

cost_per_page_cents: int
"""стоимость печати одноко листа в коп."""
