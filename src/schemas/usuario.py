from pydantic import BaseModel


class usuarioCreate(BaseModel):
    username: str
    password: str
    email: str
    name: str
    lastname: str
    
    class Config:
        orm_mode = True