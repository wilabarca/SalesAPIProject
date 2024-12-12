from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
from passlib.context import CryptContext
from starlette.middleware.cors import CORSMiddleware

# Inicialización de FastAPI
app = FastAPI()

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración de la base de datos MySQL
DATABASE_URL = "mysql+pymysql://root:@localhost/goflow"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Contexto de Hashing de contraseñas con passlib
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Modelo de la base de datos
class Usuario(Base):
    __tablename__ = "usuarios"
    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100), index=True)
    correo = Column(String(100), unique=True, index=True)
    password = Column(String(100))
    tipo = Column(String(50), default="usuario")  # "usuario" o "colaborador"

# Crear tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Pydantic modelo de datos de entrada para el registro de usuario
class RegistroUsuario(BaseModel):
    firstName: str = Field(..., min_length=2, max_length=50)
    lastName: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    confirmPassword: str = Field(..., min_length=6)
    tipo: str = Field(..., pattern="^(usuario|colaborador)$")

    class Config:
        orm_mode = True

# Función para obtener la base de datos
def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Función para verificar y hashear la contraseña
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# Endpoint para obtener usuarios por tipo
@app.get("/usuarios/{tipo}")
def obtener_usuarios_por_tipo(tipo: str, db: Session = Depends(get_db)):
    if tipo not in ["usuario", "colaborador"]:
        raise HTTPException(status_code=400, detail="Tipo de usuario inválido.")
    usuarios = db.query(Usuario).filter(Usuario.tipo == tipo).all()
    return usuarios

# Endpoint para registrar un nuevo usuario
@app.post("/registrar/")
async def registrar_usuario(data: RegistroUsuario, db: Session = Depends(get_db)):
    if data.password != data.confirmPassword:
        raise HTTPException(status_code=400, detail="Las contraseñas no coinciden.")
    
    usuario_existente = db.query(Usuario).filter(Usuario.correo == data.email).first()
    if usuario_existente:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")

    hashed_password = hash_password(data.password)
    nombre_completo = f"{data.firstName} {data.lastName}"
    nuevo_usuario = Usuario(
        nombre=nombre_completo,
        correo=data.email,
        password=hashed_password,
        tipo=data.tipo,
    )
    try:
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Error al guardar el usuario")

    return {
        "mensaje": f"{data.tipo.capitalize()} registrado con éxito",
        "usuario": {"nombre": nombre_completo, "correo": data.email, "tipo": data.tipo},
    }

# Endpoint para iniciar sesión
@app.post("/login/")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(Usuario).filter(Usuario.correo == form_data.username).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, usuario.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Redirigir según el tipo de usuario
    if usuario.tipo == "usuario":
        return {"mensaje": "Inicio de sesión exitoso", "vista": "Usuario Home"}
    elif usuario.tipo == "colaborador":
        return {"mensaje": "Inicio de sesión exitoso", "vista": "Colaborador Dashboard"}
