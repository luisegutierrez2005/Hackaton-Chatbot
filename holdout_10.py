"""Diez paráfrasis simuladas separadas de la batería de desarrollo."""

from contextlib import closing
import os
import sys

import app
import smart
from evaluar_simulacion import assess


CASES = [
    ("H01", "Soy egresado con título; necesito una certificación académica.", "verified_public", "registro-y-control", "certificate_graduates"),
    ("H02", "¿Puedo pedir una copia impresa de mi certificado?", "verified_public", "registro-y-control", "certificate_physical"),
    ("H03", "¿Qué pasa si falto a más de tres de cada diez clases?", "verified_public", "Reglamento_general", "attendance"),
    ("H04", "¿Cuántos días dan para conseguir una copia de acta?", "verified_public", "registro-y-control", "diploma_copy"),
    ("H05", "¿Dónde puedo obtener tutoría de estadística en el CESA?", "verified_public", "centros-de-apoyo", "suma"),
    ("H06", "¿Puedo pedirle a DIGA que revise mi presentación oral?", "verified_public", "centros-de-apoyo", "diga"),
    ("H07", "¿Mi beca está aprobada?", "abstain", "", None),
    ("H08", "¿Dónde miro mis calificaciones finales?", "abstain", "", None),
    ("H09", "¿Cuándo termina el periodo de clases 2026-2?", "verified_public", "calendario-academico-pregrado", "calendar_last_2026_2"),
    ("H10", "¿Ya publicaron el calendario de 2027-1?", "abstain", "", None),
]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.environ["ENABLE_DIRECT_CESA_FETCH"] = "0"
    os.environ["ENABLE_COMPOSIO_APIFY"] = "0"
    with closing(app.connect()) as conn:
        app.seed_local(conn)
        passed_count = 0
        for identifier, question, expected, url, fact in CASES:
            result = smart.answer_question(question, conn)
            passed, status, urls = assess(expected, url, result, fact)
            passed_count += passed
            print(f"{identifier} | {'OK' if passed else 'FALLO'} | {expected} → {status} | {urls}")
            if not passed:
                print("    " + result.get("answer", "")[:220])
    print(f"TOTAL {passed_count}/{len(CASES)}")
