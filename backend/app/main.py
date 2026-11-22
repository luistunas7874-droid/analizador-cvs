from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select

from .auth import crear_token, hashear, usuario_actual, verificar
from .database import crear_tablas, get_session
from .models import LoginIn, RegistroIn, TokenOut, Usuario, UsuarioOut


@asynccontextmanager
async def lifespan(app: FastAPI):
    crear_tablas()  # crea las tablas al arrancar si no existen
    yield


app = FastAPI(title="Analizador de CVs API", lifespan=lifespan)

# Permite que el front-end se conecte desde otro puerto
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # luego lo cambiamos por la URL real del front-end
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def inicio():
    return {"mensaje": "API del Analizador de CVs funcionando"}


@app.post("/auth/register", response_model=UsuarioOut, status_code=201)
def registrar(datos: RegistroIn, session: Session = Depends(get_session)):
    email = datos.email.strip().lower()
    existe = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if existe:
        raise HTTPException(status_code=400, detail="Ese correo ya esta registrado")
    usuario = Usuario(email=email, password_hash=hashear(datos.password))
    session.add(usuario)
    session.commit()
    session.refresh(usuario)
    return usuario


@app.post("/auth/login", response_model=TokenOut)
def login(datos: LoginIn, session: Session = Depends(get_session)):
    email = datos.email.strip().lower()
    usuario = session.exec(select(Usuario).where(Usuario.email == email)).first()
    if not usuario or not verificar(datos.password, usuario.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contrasena incorrectos")
    return TokenOut(access_token=crear_token(usuario.id))


@app.get("/auth/me", response_model=UsuarioOut)
def mi_perfil(usuario: Usuario = Depends(usuario_actual)):
    return usuario
