import logging

from aio_pika import Connection, DeliveryMode, ExchangeType, Message, connect
from pydantic import BaseModel

from app.core.config import settings

logger = logging.getLogger(__name__)


class RmqMessage(BaseModel):
    message_type: str
    body: dict


class PikaClient:
    def __init__(self):
        self.connection: Connection = None

    async def get_connection(self) -> Connection:
        return await connect(
            host=settings.RMQ_HOST,
            login=settings.RMQ_USER,
            password=settings.RMQ_PASS,
            port=5672,
        )

    async def send_msg(
        self, exchange_name: str, routing_key: str, msg: RmqMessage
    ) -> None:
        if not self.connection:
            connection = await self.get_connection()
            self.connection = connection

        connection = self.connection

        channel = await connection.channel()
        exchange = await channel.declare_exchange(exchange_name, ExchangeType.FANOUT,)

        message_body = bytes(msg.json(), "utf-8")
        message = Message(message_body, delivery_mode=DeliveryMode.PERSISTENT)

        await exchange.publish(message, routing_key)
