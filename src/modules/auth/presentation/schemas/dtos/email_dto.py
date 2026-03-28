from src.modules.core.domain.dtos.email.email_dtos import SendEmailDTO
from src.modules.core.presentation.http.schemas.pydantic.email_schema import SendEmailRequestBody


class SendEmailPayloadDTO:
    def to_usecase(self, payload: SendEmailRequestBody) -> SendEmailDTO:
        return SendEmailDTO(
            to=payload.to,
            subject=payload.subject,
            text_body=payload.text_body,
            html_body=payload.html_body,
            cc=payload.cc,
            bcc=payload.bcc,
            reply_to=payload.reply_to,
        )
