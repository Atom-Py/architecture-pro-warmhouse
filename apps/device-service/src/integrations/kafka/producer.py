from aiokafka import AIOKafkaProducer
from msgspec import Struct
from msgspec.json import Encoder

from config.settings import settings


class KafkaProducer:
    def __init__(self) -> None:
        self._producer: AIOKafkaProducer | None = None
        self._encoder = Encoder()

    async def start(self) -> None:
        self._producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA.BOOTSTRAP_SERVERS)
        await self._producer.start()

    async def stop(self) -> None:
        if self._producer is not None:
            await self._producer.stop()
            self._producer = None

    async def publish(self, topic: str, event: Struct) -> None:
        if self._producer is None:
            raise RuntimeError("kafka producer is not started")
        await self._producer.send_and_wait(topic, self._encoder.encode(event))


producer = KafkaProducer()
