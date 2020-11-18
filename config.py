import os
from typing import Dict, Any


class Config:
    MAIL_FROM = os.getenv('MAIL_FROM')
    MAIL_TO = os.getenv('MAIL_TO')
    API_ID = os.getenv('API_ID')
    API_HASH = os.getenv('API_HASH')
    SESSION_STRING = os.getenv('SESSION_STRING')
    TIMEZONE = int(os.getenv('TIMEZONE', 0))
    
    FILTERS: Dict[str, Any] = {}
    if 'CHATS' in os.environ:
        FILTERS['chats'] = eval(os.getenv('CHATS'))