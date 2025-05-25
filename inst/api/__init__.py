from .routers import main_router
from .core import app


app.include_router(main_router)