from pydantic import EmailStr, Field
from typing import List, Optional


class Email:
    sender: EmailStr
    recipients: List[EmailStr]
    subject: str
    content: str
    attach: Optional[bytes]

    def __init__(self, sender: EmailStr, recipients: List[EmailStr], subject: str, content: str,
                 attach: Optional[bytes]) -> None:
        self.sender = sender
        self.recipients = recipients
        self.subject = subject
        self.content = content
        self.attach = attach

