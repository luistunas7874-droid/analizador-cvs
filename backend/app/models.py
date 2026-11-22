from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


def ahora():
    return datetime.now(timezone.utc)


# ---------- Tablas ----------
class Usuario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    password_hash: str
    creado: datetime = Field(default_factory=ahora)


class Analisis(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    vacante: str
    compatibility_score: int
    resultado_json: str  # el JSON completo que devuelve la IA, guardado como texto
    created_at: datetime = Field(default_factory=ahora)


class CV(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    usuario_id: int = Field(foreign_key="usuario.id", index=True)
    nombre_archivo: str
    tamano_bytes: int
    analisis_id: Optional[int] = Field(default=None, foreign_key="analisis.id")
    created_at: datetime = Field(default_factory=ahora)


# ---------- Formatos de la API ----------
class RegistroIn(SQLModel):
    email: str
    password: str = Field(min_length=6)


class LoginIn(SQLModel):
    email: str
    password: str


class TokenOut(SQLModel):
    access_token: str
    token_type: str = "bearer"


class UsuarioOut(SQLModel):
    id: int
    email: str
