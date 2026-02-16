from fastapi import FastAPI
from config import settings
from api.routes import router


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
)

app.include_router(router)
