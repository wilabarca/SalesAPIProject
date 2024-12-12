from pydantic import BaseModel

class colaboradorCreate(BaseModel):
    telefono: str
    dedicacion: str
    email: str
    name: str
    lastname: str
    
    class Config:
        orm_mode = True