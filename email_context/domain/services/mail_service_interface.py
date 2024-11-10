from abc import ABC, abstractmethod
from email_context.domain.email import Email


class MailServiceInterface(ABC):

    @abstractmethod
    def send_mail(self, mail: Email) -> str:
        pass
