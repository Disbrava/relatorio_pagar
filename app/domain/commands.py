from pydantic import BaseModel, ConfigDict


class Command(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    pass


