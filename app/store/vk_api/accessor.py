import typing
import random
from urllib.parse import urlencode, urljoin

import aiohttp
from aiohttp.client import ClientSession

from app.base.base_accessor import BaseAccessor
from app.store.vk_api.dataclasses import Message, Update, UpdateObject, UpdateMessage
from app.store.vk_api.poller import Poller

if typing.TYPE_CHECKING:
    from app.web.app import Application

API_VERSION = "5.131"
API_PATH = "https://api.vk.com/method/"


class VkApiAccessor(BaseAccessor):
    def __init__(self, app: "Application", *args, **kwargs):
        super().__init__(app, *args, **kwargs)
        self.session: ClientSession | None = None
        self.key: str | None = None
        self.server: str | None = None
        self.poller: Poller | None = None
        self.ts: int | None = None

    async def connect(self, app: "Application"):
        self.session = ClientSession(connector=aiohttp.TCPConnector(ssl=False))
        self.poller = Poller(self.app.store)
        await self._get_long_poll_service()
        await self.poller.start()

    async def disconnect(self, app: "Application"):
        if self.session:
            await self.session.close()
        if self.poller:
            await self.poller.stop()

    @staticmethod
    def _build_query(host: str, method: str, params: dict) -> str:
        params.setdefault("v", API_VERSION)
        return f"{urljoin(host, method)}?{urlencode(params)}"

    async def _get_long_poll_service(self):
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="groups.getLongPollServer",
                params={
                    "access_token": self.app.config.bot.token,
                    "group_id": self.app.config.bot.group_id,
                },
            )
        ) as response:
            response_body = await response.json()
            self.logger.info(response_body)
            data = response_body["response"]
            self.key = data["key"]
            self.server = data["server"]
            self.ts = data["ts"]

    async def poll(self):
        async with self.session.get(
            self._build_query(
                host=self.server,
                method="",
                params={"act": "a_check", "key": self.key, "ts": self.ts, "wait": 25},
            )
        ) as response:
            response_body = await response.json()
            self.logger.info(response_body)
            self.ts = response_body["ts"]
            return [
                Update(
                    type=update["type"],
                    object=UpdateObject(
                        message=UpdateMessage(
                            from_id=update["object"]["message"]["from_id"],
                            text=update["object"]["message"]["text"],
                            id=update["object"]["message"]["id"],
                        )
                    ),
                )
                for update in response_body["updates"]
                if update["type"] == "message_new"
            ]

    async def send_message(self, message: Message) -> None:
        async with self.session.get(
            self._build_query(
                host=API_PATH,
                method="messages.send",
                params={
                    "user_id": message.user_id,
                    "random_id": random.randint(1, 2**32),
                    "peer_id": "-" + str(self.app.config.bot.group_id),
                    "message": message.text,
                    "access_token": self.app.config.bot.token,
                },
            )
        ) as response:
            response_body = await response.json()
            self.logger.info(response_body)
