"""Quince preguntas de prueba redactadas por el equipo; no son logs de estudiantes."""

from contextlib import closing
import json
import sys
import urllib.request

import app
import smart


CASES = [
    ("Certificado activo", "¿Cómo solicito un certificado de estudios si soy estudiante activo?"),
    ("Certificado graduado", "¿Cómo solicito un certificado si ya me gradué?"),
    ("Inasistencias", "¿Con cuántas inasistencias pierdo una materia?"),
    ("Incapacidad", "¿Una incapacidad médica elimina mis faltas?"),
    ("Vigencia reglamento", "¿Desde cuándo rige el reglamento estudiantil de 2026?"),
    ("Créditos malla", "¿Cuántos créditos tiene la carrera según la malla?"),
    ("Séptimo semestre", "¿Qué materias hay en séptimo semestre?"),
    ("Investigación de Operaciones", "¿Cuántos créditos tiene Investigación de Operaciones?"),
    ("Centro DIGA", "¿Dónde queda el Centro DIGA y cómo pido una cita?"),
    ("Consejería", "¿Qué apoyo psicológico ofrece el CESA?"),
    ("Próximo semestre", "¿Cuándo comienza el próximo semestre de pregrado?"),
    ("Becas", "¿Qué becas y financiación ofrece el CESA?"),
    ("Pizza Fiamma", "¿Dónde está la máquina de pizzas Fiamma y cuál es su horario?"),
    ("Notas privadas", "¿Cuáles son mis notas?"),
    ("Horario privado", "¿Cuál es mi horario de clases mañana?"),
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    use_http = "--http" in sys.argv
    with closing(app.connect()) as conn:
        if not use_http:
            app.seed_local(conn)
        for number, (label, question) in enumerate(CASES, 1):
            if use_http:
                request = urllib.request.Request(
                    "http://127.0.0.1:8765/api/chat",
                    data=json.dumps({"question": question}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(request, timeout=5) as response:
                    result = json.load(response)
            else:
                result = smart.answer_question(question, conn)
            urls = ", ".join(s.get("url", "") for s in result.get("sources", []))
            print(f"{number:02d} | {label} | {result['status']} | {urls}")
            print(result["answer"].replace("\n", " "))
