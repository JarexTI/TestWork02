from fastapi import FastAPI

from app.routers.auth import router as router_auth
from app.routers.tasks import router as router_task


def get_app() -> FastAPI:
    app = FastAPI(
        title='Task service',
        version='1.0.0'
    )

    @app.get('/')
    def read_root() -> dict[str, str]:
        return {'message': 'API is working'}

    app.include_router(
        router_auth,
        prefix='/auth',
        tags=['Auth']
    )
    app.include_router(
        router_task,
        prefix='/tasks',
        tags=['Tasks']
    )

    return app


app = get_app()
