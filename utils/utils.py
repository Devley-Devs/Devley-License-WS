import time, uuid
from fastapi import WebSocket

class LicenseObject:
    def __init__(self, license_key: str = ''):
        self.license_key: str = license_key
        splitted_data: list = license_key.split('_') if license_key else []
        self.transaction_id: str =  splitted_data[0] if len(splitted_data) > 0 else ''
        self.user_id: str = splitted_data[1] if len(splitted_data) > 1 else ''
        self.uuid: str = splitted_data[2] if len(splitted_data) > 2 else ''

class ClientWSObject:
    def __init__(self, ws: WebSocket):
        self.ws: WebSocket = ws
        self.connect_time: int = int(time.time())
        self.session_id: str = str(uuid.uuid4())

    def __iter__(self):
        yield "connect_time", self.connect_time
        yield "session_id", self.session_id