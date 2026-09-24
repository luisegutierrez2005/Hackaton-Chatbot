"""Evalúa casos simulados contra el backend sin activar búsquedas externas.

No es un verificador semántico de la veracidad: compara estado y URL esperados.
Las afirmaciones de las fuentes requieren la matriz de revisión humana.
"""

import json
import os
import sys
import urllib.request
from contextlib import closing

import app
import smart
from simulacion_50 import CASES, EXPECTED_FACTS


def assess(expected_status, expected_url, result, expected_fact=None):
    status = result.get("status")
    urls = [source.get("url", "") for source in result.get("sources", [])]
    if expected_status == "abstain":
        passed = status == "no_match" and (
            "no tengo" in result.get("answer", "").lower()
            or "no puedo" in result.get("answer", "").lower()
            or "no encontr" in result.get("answer", "").lower())
    else:
        passed = (status == expected_status
                  and (not expected_url or any(expected_url in url for url in urls))
                  and (not expected_fact or result.get("fact_id") == expected_fact))
    return passed, status, urls


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    via_http = "--http" in sys.argv
    # The evaluation must be reproducible and must not trigger external calls.
    os.environ["ENABLE_COMPOSIO_APIFY"] = "0"
    os.environ["ENABLE_DIRECT_CESA_FETCH"] = "0"
    records = []
    with closing(app.connect()) as conn:
        if not via_http:
            app.seed_local(conn)
        for identifier, category, question, expected_status, expected_url in CASES:
            if via_http:
                request = urllib.request.Request(
                    "http://127.0.0.1:8765/api/chat",
                    data=json.dumps({"question": question}).encode("utf-8"),
                    headers={"Content-Type": "application/json"}, method="POST")
                with urllib.request.urlopen(request, timeout=8) as response:
                    result = json.load(response)
            else:
                result = smart.answer_question(question, conn)
            passed, status, urls = assess(expected_status, expected_url, result,
                                          EXPECTED_FACTS.get(identifier))
            records.append({"id": identifier, "category": category, "question": question,
                            "expected": expected_status, "status": status,
                            "passed": passed, "urls": urls, "answer": result.get("answer", "")})
            print(f"{identifier} | {category:13} | {'OK' if passed else 'FALLO'} | {expected_status} → {status}")
            if not passed:
                print("    " + result.get("answer", "").replace("\n", " ")[:280])
    print(f"TOTAL {sum(row['passed'] for row in records)}/{len(records)}")
