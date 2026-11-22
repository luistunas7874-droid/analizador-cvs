import os
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlmodel import Session

from .database import get_session
from .models import Usuario

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "clave-solo-para-desarrollo-cambiala-pronto-123456")
ALGORITHM = "HS256"
EXPIRA_MINUTOS = 60 * 24  # el token dura 1 dia

bearer = HTTPBearer()


def hashear(password: str) -> str:
    return bcrypt.hashpw(password.encode()[:72], bcrypt.gensalt()).decode()


def verificar(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode()[:72], password_hash.encode())


def crear_token(usuario_id: int) -> str:
    payload = {
        "sub": str(usuario_id),
        "exp": datetime.now(timezone.utc) + timedelta(minutes=EXPIRA_MINUTOS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def usuario_actual(
    credenciales: HTTPAuthorizationCredentials = Depends(bearer),
    session: Session = Depends(get_session),
) -> Usuario:
    error = HTTPException(status_code=401, detail="Token invalido o expirado")
    try:
        payload = jwt.decode(credenciales.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        usuario_id = int(payload["sub"])
    except (jwt.PyJWTError, KeyError, ValueError):
        raise error
    usuario = session.get(Usuario, usuario_id)
    if not usuario:
        raise error
    return usuario
