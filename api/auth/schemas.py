from pydantic import BaseModel


class ActivateUserSchema(BaseModel):
    token: str
