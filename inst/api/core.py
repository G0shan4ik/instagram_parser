from fastapi import FastAPI

from os import getenv
from dotenv import load_dotenv


load_dotenv()

app = FastAPI(
    debug=bool(getenv("DEBUG", True)),
)

__all__ = ["app"]