from abc import ABC, abstractmethod
from typing import Any

from email_context.domain.query import Query


class QueryHandler(ABC):

    @abstractmethod
    async def handler(self, query: Query) -> Any:
        pass

