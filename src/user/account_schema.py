from pydantic import (
    BaseModel,
    EmailStr,
    Field,
    model_validator,
)


class UpdateAccountSchema(BaseModel):
    current_password: str = Field(min_length=1, max_length=72)

    new_email: EmailStr | None = None

    new_password: str | None = Field(
        default=None,
        min_length=8,
        max_length=72,
    )

    @model_validator(mode="after")
    def validate_changes(self):
        if self.new_email is None and self.new_password is None:
            raise ValueError(
                "Enter a new email or a new password"
            )

        return self
