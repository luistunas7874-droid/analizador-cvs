def analizar(cv_bytes: bytes, vacante: str) -> dict:
    """AQUI conecta la persona C: extraer el texto del PDF y llamar a la IA.
    Debe devolver un dict con estas mismas claves."""
    return {
        "compatibility_score": 70,
        "summary": "Analisis de ejemplo, todavia sin IA.",
        "strengths": ["Ejemplo de fortaleza"],
        "weaknesses": ["Ejemplo de debilidad"],
        "missing_keywords": ["ejemplo"],
        "suggestions": ["Ejemplo de sugerencia"],
    }
