from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ManagerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    department: str = Field(default="General", max_length=100)


class ManagerResponse(BaseModel):
    id: int
    user_id: int
    name: str
    department: str
    email: EmailStr

    model_config = ConfigDict(from_attributes=True)
