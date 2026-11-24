import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.concurrency import run_in_threadpool
from sqlmodel import Session, select

from .auth import usuario_actual
from .database import get_session
from .ia import analizar
from .models import CV, Analisis, Usuario

router = APIRouter(prefix="/analyses", tags=["analyses"])
router_cvs = APIRouter(prefix="/cvs", tags=["cvs"])


def armar(a: Analisis) -> dict:
    datos = json.loads(a.resultado_json)
    datos["id"] = a.id
    datos["created_at"] = a.created_at.isoformat()
    datos.setdefault("match_percentage", a.compatibility_score)
    datos.setdefault("compatibility_score", a.compatibility_score)
    return datos


@router.post("", status_code=201)
async def crear_analisis(
    vacante: str = Form(...),
    cv: UploadFile = File(...),
    usuario: Usuario = Depends(usuario_actual),
    session: Session = Depends(get_session),
):
    if not (cv.filename or "").lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="El CV debe ser un PDF")
    contenido = await cv.read()
    try:
        resultado = await run_in_threadpool(analizar, vacante, contenido)
    except ValueError as e:  # PDF ilegible o sin texto
        raise HTTPException(status_code=422, detail=str(e))
    except RuntimeError as e:  # falla del servicio de IA
        raise HTTPException(status_code=502, detail=str(e))
    resultado["archivo"] = cv.filename

    registro = Analisis(
        usuario_id=usuario.id,
        vacante=vacante,
        compatibility_score=int(resultado["match_percentage"]),
        resultado_json=json.dumps(resultado, ensure_ascii=False),
    )
    session.add(registro)
    session.commit()
    session.refresh(registro)
    return armar(registro)


@router.get("")
def listar_analisis(
    usuario: Usuario = Depends(usuario_actual),
    session: Session = Depends(get_session),
):
    filas = session.exec(
        select(Analisis)
        .where(Analisis.usuario_id == usuario.id)
        .order_by(Analisis.created_at.desc())
    ).all()
    return [armar(f) for f in filas]


@router.get("/{analisis_id}")
def detalle_analisis(
    analisis_id: int,
    usuario: Usuario = Depends(usuario_actual),
    session: Session = Depends(get_session),
):
    fila = session.get(Analisis, analisis_id)
    if not fila or fila.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    return armar(fila)


@router.delete("/{analisis_id}", status_code=204)
def borrar_analisis(
    analisis_id: int,
    usuario: Usuario = Depends(usuario_actual),
    session: Session = Depends(get_session),
):
    fila = session.get(Analisis, analisis_id)
    if not fila or fila.usuario_id != usuario.id:
        raise HTTPException(status_code=404, detail="Analisis no encontrado")
    for cv_fila in session.exec(select(CV).where(CV.analisis_id == analisis_id)).all():
        cv_fila.analisis_id = None
        session.add(cv_fila)
    session.delete(fila)
    session.commit()


@router_cvs.get("")
def listar_cvs():
    return []