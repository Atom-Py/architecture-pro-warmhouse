from robyn import Headers, Response, SubRouter

health_router = SubRouter(prefix="/health")


@health_router.get("")
def health() -> Response:
    return Response(
        status_code=200,
        headers=Headers({"Content-Type": "application/json"}),
        body=b'{"status":"ok"}',
    )
