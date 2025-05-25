from pydantic import BaseModel


class BaseData(BaseModel):
    links: list[str]
    per_second: int = 1
    print_data: bool = False


