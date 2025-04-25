from fastapi import FastAPI

from app.routers.auth import router as router_auth
from app.routers.tasks import router as router_task


def create_app() -> FastAPI:
    """
    Создание экземпляра FastAPI приложения.
    """
    app = FastAPI(
        title='Task Service',
        version='1.0.0',
        docs_url='/docs',
        redoc_url='/redoc'
    )

    @app.get('/', tags=['Root'])
    async def read_root() -> dict[str, str]:
        """
        Проверка состояния API.
        """
        return {'message': 'API is working'}

    app.include_router(router_auth)
    app.include_router(router_task)

    return app


app = create_app()
