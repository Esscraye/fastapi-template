from fastapi import FastAPI
from core.config import get_settings
from core.logging_config import setup_logging
from v1.api import api_router
import os

# Crée le dossier logs si nécessaire
def ensure_log_dir():
    if not os.path.exists("logs"):
        os.makedirs("logs")

ensure_log_dir()
setup_logging()

settings = get_settings()

app = FastAPI(title=settings.APP_NAME, debug=settings.DEBUG)

# Monter les routes versionnées
def include_routers(app: FastAPI):
    app.include_router(api_router, prefix="/v1")

include_routers(app)

# Racine simple
def root():
    return {"msg": f"Welcome to {settings.APP_NAME}"}

app.get("/")(root)