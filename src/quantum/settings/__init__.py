import os

load_production = os.getenv('FOPF_PRINT_ENVIRONMENT') == 'prod'

# да, через одно место, зато работает))
if load_production:
    from ._prod import *  # noqa
else:
    from ._dev import *  # noqa
