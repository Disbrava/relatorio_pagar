from abc import ABC, abstractmethod
from typing import Any

from email_context.domain.commands import Command


class CommandHandler(ABC):

    @abstractmethod
    def handler(self, command: Command) -> Any:
        pass
