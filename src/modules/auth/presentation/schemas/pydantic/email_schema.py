from pydantic import BaseModel


class SendEmailRequestBody(BaseModel):
    to: list[str]
    subject: str
    text_body: str | None = None
    html_body: str | None = None
    cc: list[str] | None = None
    bcc: list[str] | None = None
    reply_to: str | None = None
