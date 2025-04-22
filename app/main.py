from fastapi import FastAPI


def get_app() -> FastAPI:
    app = FastAPI(
        title='Task service',
        version='1.0.0'
    )

    @app.get('/')
    def read_root() -> dict[str, str]:
        return {'message': 'API is working'}

    return app


app = get_app()
