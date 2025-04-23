import os
from amocrm.v2 import tokens
from config import AMO_CLIENT_ID, AMO_CLIENT_SECRET, AMO_SUBDOMAIN, AMO_CODE

def init_crm():
    token_file = "tokens.json"  # это файл, который будет использовать FileTokensStorage()

    tokens.default_token_manager(
        client_id=AMO_CLIENT_ID,
        client_secret=AMO_CLIENT_SECRET,
        subdomain=AMO_SUBDOMAIN,
        redirect_url="https://ya.ru",
        storage=tokens.FileTokensStorage(token_file),
    )

    if not os.path.exists(token_file):
        # Выполняем только при первом запуске, когда токенов ещё нет
        tokens.default_token_manager.init(
            code=AMO_CODE,
            skip_error=True
        )