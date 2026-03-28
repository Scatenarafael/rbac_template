# from src.modules.core.domain.dtos.users.user_dtos import PayloadCreateUserDTO, PayloadUpdateUserDTO
# from src.modules.core.presentation.http.schemas.pydantic.user_schema import PayloadUpdateUser, UserRequestBody


# class RegisterUserPayloadDTO:
#     def to_usecase(self, payload: UserRequestBody) -> RegisterUserUseCasePayload:
#         return PayloadCreateUserDTO(
#             first_name=payload.first_name,
#             last_name=payload.last_name,
#             email=payload.email,
#             password=payload.password,
#         )


# class UpdateUserPayloadDTO:
#     def to_usecase(self, payload: PayloadUpdateUser) -> PayloadUpdateUserDTO:
#         return PayloadUpdateUserDTO(
#             first_name=payload.first_name,
#             last_name=payload.last_name,
#             email=payload.email,
#             password=payload.password,
#             active=payload.active,
#         )
