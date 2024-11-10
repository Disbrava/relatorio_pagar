from email_context.container import Container
from .settings import Settings

settings = Settings()
container = Container()

container.config.from_dict(settings.model_dump())
# container.example_context.config.from_pydantic(settings)  # Define other contexts configs
container.database()
