from sqlalchemy.orm import session
from Models.usuario import usuario
from Models.persona import persona

def create_usuario(db: session, username:str, password: str, name:str, lastname:str, email:str):
    persona = persona(name= name, lastname=lastname, email=email)
    db.add(persona)
    db.commit()
    db.refresh()
    
    new_usuario = usuario(username=username, password=password, password=password, persona_id=persona.id)
    db.add(new_usuario)
    db.commit()
    db.refresh(new_usuario)

return new_usuario    