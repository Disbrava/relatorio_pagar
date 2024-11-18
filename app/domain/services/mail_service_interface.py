from abc import ABC, abstractmethod
from app.domain.email import Email


class MailServiceInterface(ABC):

    @abstractmethod
    def send_mail(self, mail: Email) -> str:
        pass
