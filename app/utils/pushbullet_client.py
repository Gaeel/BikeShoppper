from requests import Session
from logging import getLogger

class PushBulletClient:
    def __init__(self, token: str) -> None:
        self.session = Session()
        self.session.headers.update(**self.session.headers, **{"Access-Token": token, "Content-Type": "application/json"})
        self.logger = getLogger()

    def notify(self, title: str, message: str, ):
        r = self.session.post(
            url='https://api.pushbullet.com/v2/pushes',
            json={"body": message,"title": title, "type":"note"}
        )
        r.raise_for_status()
        return r.json()