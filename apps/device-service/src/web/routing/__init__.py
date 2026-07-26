from robyn import SubRouter

from web.routing.devices import devices_router
from web.routing.health import health_router

root_router = SubRouter(prefix="")
root_router.include_router(health_router)
root_router.include_router(devices_router)
