from abc import ABC, abstractmethod
from typing import Any

from app.domain.commands import Command


class CommandHandler(ABC):

    @abstractmethod
    async def handler(self, command: Command) -> Any:
        pass
