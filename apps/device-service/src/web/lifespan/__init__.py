from msgspec.json import Encoder
from robyn import Robyn

from infra.db.engine import engine
from integrations.kafka import status_consumer
from integrations.kafka.producer import producer
from models.db.sqlalchemy import Base
from services.seed import seed_device_types


def register(app: Robyn) -> None:
    app.inject_global(msgspec_json_encoder=Encoder())

    @app.startup_handler
    async def startup() -> None:
        async with engine.begin() as connection:
            await connection.run_sync(Base.metadata.create_all)
        await seed_device_types()
        await producer.start()
        status_consumer.start()

    @app.shutdown_handler
    async def shutdown() -> None:
        await status_consumer.stop()
        await producer.stop()
        await engine.dispose()
