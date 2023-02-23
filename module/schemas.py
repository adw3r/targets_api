from pydantic import BaseModel


class Email(BaseModel):
    email: str
    source: str

    class Config:
        orm_mode = True
