import os

load_production = os.getenv('FOPF_PRINT_ENVIRONMENT') == 'PROD'

# да, через одно место, зато работает))
if load_production:
    from quantum.all_settings.prod import *  # noqa
else:
    from quantum.all_settings.dev import *  # noqa
