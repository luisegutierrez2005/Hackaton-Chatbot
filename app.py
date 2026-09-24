"""Local, cited CESA information assistant. Python 3.10+; no LLM or login."""

from __future__ import annotations

import argparse
import html
import importlib.util
import json
import os
import re
import shutil
import sqlite3
import sys
import threading
import unicodedata
import urllib.parse
import urllib.request
import urllib.robotparser
from contextlib import closing
from datetime import datetime, timezone
from html.parser import HTMLParser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from knowledge import (COURSES, CURRICULUM_SOURCE, EXPECTED_CREDITS, FACTS,
                       PUBLIC_PAGES, REGULATION_URL)

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DB_PATH = DATA / "cesa.sqlite3"
ASSETS = HERE / "assets"
USER_AGENT = "CESA-Hackaton-Student-Research/0.1 (local prototype; public pages only)"
SOURCE_PDF = Path(os.getenv("CESA_MALLA_PDF", str(ASSETS / "malla-source.pdf")))
NIDO_URL = "https://experience.elluciancloud.com/cdesdac/"
ROBOTS_URL = "https://www.cesa.edu.co/robots.txt"
WEB_LOCK = threading.Lock()


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def normalize(value: str) -> str:
    value = unicodedata.normalize("NFKD", value.lower())
    return "".join(c for c in value if not unicodedata.combining(c))


def connect() -> sqlite3.Connection:
    DATA.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def create_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS sources (
      id INTEGER PRIMARY KEY, url TEXT NOT NULL UNIQUE, title TEXT NOT NULL,
      type TEXT NOT NULL, provenance TEXT NOT NULL, status TEXT NOT NULL,
      checked_at TEXT, note TEXT
    );
    CREATE TABLE IF NOT EXISTS facts (
      id TEXT PRIMARY KEY, question TEXT NOT NULL, aliases TEXT NOT NULL,
      answer TEXT NOT NULL, source_id INTEGER NOT NULL,
      citation TEXT NOT NULL, status TEXT NOT NULL, topic TEXT NOT NULL,
      FOREIGN KEY(source_id) REFERENCES sources(id)
    );
    CREATE TABLE IF NOT EXISTS courses (
      semester INTEGER NOT NULL, title TEXT NOT NULL, credits INTEGER NOT NULL,
      source_id INTEGER NOT NULL, PRIMARY KEY(semester,title),
      FOREIGN KEY(source_id) REFERENCES sources(id)
    );
    CREATE TABLE IF NOT EXISTS passages (
      id INTEGER PRIMARY KEY, source_id INTEGER NOT NULL, section TEXT NOT NULL,
      body TEXT NOT NULL, FOREIGN KEY(source_id) REFERENCES sources(id)
    );
    CREATE TABLE IF NOT EXISTS web_fetches (
      id INTEGER PRIMARY KEY, url TEXT NOT NULL, fetched_at TEXT NOT NULL
    );
    CREATE VIRTUAL TABLE IF NOT EXISTS passage_search USING fts5(
      body, content='passages', content_rowid='id',
      tokenize='unicode61 remove_diacritics 2'
    );
    CREATE TRIGGER IF NOT EXISTS passages_ai AFTER INSERT ON passages BEGIN
      INSERT INTO passage_search(rowid, body) VALUES (new.id, new.body);
    END;
    CREATE TRIGGER IF NOT EXISTS passages_ad AFTER DELETE ON passages BEGIN
      INSERT INTO passage_search(passage_search, rowid, body)
      VALUES ('delete', old.id, old.body);
    END;
    """)


def upsert_source(conn, url, title, kind, provenance, status, note="") -> int:
    conn.execute("""
      INSERT INTO sources(url,title,type,provenance,status,checked_at,note)
      VALUES (?,?,?,?,?,?,?) ON CONFLICT(url) DO UPDATE SET
      title=excluded.title, type=excluded.type,
      provenance=excluded.provenance, status=excluded.status,
      checked_at=excluded.checked_at, note=excluded.note
    """, (url, title, kind, provenance, status, now(), note))
    return conn.execute("SELECT id FROM sources WHERE url=?", (url,)).fetchone()[0]


def seed_local(conn: sqlite3.Connection) -> None:
    create_schema(conn)
    ASSETS.mkdir(exist_ok=True)
    malla = ASSETS / "malla-curricular-2025.pdf"
    if SOURCE_PDF.exists() and not malla.exists():
        shutil.copy2(SOURCE_PDF, malla)
    malla_id = upsert_source(
        conn, "/assets/malla-curricular-2025.pdf", "Malla curricular completa (2025)",
        "uploaded_pdf", CURRICULUM_SOURCE, "user_supplied",
        "Una página; transcripción visual de materias y créditos. Verifica si aplica a tu cohorte.",
    )
    for semester, courses in COURSES.items():
        for title, credits in courses:
            conn.execute("INSERT OR REPLACE INTO courses VALUES (?,?,?,?)",
                         (semester, title, credits, malla_id))
    for fact in FACTS:
        url = fact["url"] or "user-note:" + fact["id"]
        source_id = upsert_source(
            conn, url, fact["source"], "public" if fact["status"] == "verified_public" else "user_note",
            fact["source"], fact["status"],
            "Consultar vigencia" if fact["status"] == "user_supplied" else "",
        )
        conn.execute("""INSERT OR REPLACE INTO facts
          (id,question,aliases,answer,source_id,citation,status,topic)
          VALUES (?,?,?,?,?,?,?,?)""",
          (fact["id"], fact["question"], fact["aliases"], fact["answer"],
           source_id, fact["source"], fact["status"], fact["topic"]))
    conn.commit()


class MainTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.skip = 0
        self.main = 0
        self.all_lines: list[str] = []
        self.main_lines: list[str] = []
        self.title_parts: list[str] = []
        self.in_title = False

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip += 1
        if tag == "main":
            self.main += 1
        if tag == "title":
            self.in_title = True

    def handle_endtag(self, tag):
        if tag in {"script", "style", "noscript", "svg"}:
            self.skip = max(0, self.skip - 1)
        if tag == "main":
            self.main = max(0, self.main - 1)
        if tag == "title":
            self.in_title = False

    def handle_data(self, data):
        if self.skip:
            return
        clean = " ".join(html.unescape(data).split())
        if len(clean) < 3:
            return
        if self.in_title:
            self.title_parts.append(clean)
        self.all_lines.append(clean)
        if self.main:
            self.main_lines.append(clean)

    def result(self):
        lines = self.main_lines if len(" ".join(self.main_lines)) > 500 else self.all_lines
        return " ".join(self.title_parts)[:200], lines


def chunks(lines: list[str], max_chars=950):
    buf: list[str] = []
    size = 0
    for line in lines:
        if len(line) > max_chars:
            line = line[:max_chars]
        if size + len(line) > max_chars and buf:
            yield "\n".join(buf)
            buf, size = [], 0
        buf.append(line)
        size += len(line) + 1
    if buf:
        yield "\n".join(buf)


def replace_passages(conn, source_id: int, entries: list[tuple[str, str]]):
    conn.execute("DELETE FROM passages WHERE source_id=?", (source_id,))
    conn.executemany("INSERT INTO passages(source_id,section,body) VALUES (?,?,?)",
                     [(source_id, section, body) for section, body in entries])
    conn.commit()


def safe_get(url: str, robots: urllib.robotparser.RobotFileParser | None = None) -> tuple[bytes, str]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != "www.cesa.edu.co":
        raise ValueError("Solo se permite contenido público de www.cesa.edu.co")
    if robots and not robots.can_fetch(USER_AGENT, url):
        raise ValueError("La política robots.txt no permite esta URL")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=12) as response:
        final_url = response.geturl()
        final_host = urllib.parse.urlparse(final_url).hostname
        official_pdf_mirror = (
            url == REGULATION_URL and
            final_url == "https://bucket-cesaweb.s3.amazonaws.com/documents/Reglamento_general_de_estudiantes.pdf"
        )
        if final_host != "www.cesa.edu.co" and not official_pdf_mirror:
            raise ValueError("Redirección fuera de CESA bloqueada")
        return response.read(5_000_001), response.headers.get("Content-Type", "")


def refresh_one_public_page(conn: sqlite3.Connection, url: str) -> dict:
    """Bounded public-page pilot: one preapproved CESA URL, robots, HTML, no Nido."""
    if url not in PUBLIC_PAGES:
        raise ValueError("La URL debe estar en la lista fija de páginas públicas")
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(ROBOTS_URL)
    robots.read()
    return store_one_public_page(conn, url, robots, status="verified_public")


def store_one_public_page(conn: sqlite3.Connection, url: str,
                          robots: urllib.robotparser.RobotFileParser,
                          *, status: str = "extracted_public") -> dict:
    """Index one public CESA HTML page; caller limits discovery and request rate."""
    if status not in {"verified_public", "extracted_public"}:
        raise ValueError("Estado de fuente no permitido")
    payload, ctype = safe_get(url, robots)
    if len(payload) > 5_000_000 or "html" not in ctype.lower():
        raise ValueError("Respuesta demasiado grande o no HTML")
    parser = MainTextParser()
    parser.feed(payload.decode("utf-8", errors="replace"))
    title, lines = parser.result()
    if len(" ".join(lines)) < 300:
        raise ValueError("La página no entregó texto público suficiente")
    entries = [(f"Bloque {i}", body) for i, body in enumerate(chunks(lines), 1)]
    source_id = upsert_source(conn, url, title or url, "web_html", url, status,
                              "Extracción HTML; no revisada manualmente" if status == "extracted_public"
                              else "Extracción de una página pública fija")
    replace_passages(conn, source_id, entries)
    return {"updated": url, "passages": len(entries)}


def refresh_web(conn: sqlite3.Connection) -> dict:
    """Fetch only the fixed public source list; never access Nido/SSO."""
    report = {"updated": [], "errors": []}
    robots = urllib.robotparser.RobotFileParser()
    robots.set_url(ROBOTS_URL)
    try:
        robots.read()
    except Exception as exc:
        return {"updated": [], "errors": [f"No se pudo leer robots.txt: {exc}"]}
    for url in PUBLIC_PAGES:
        try:
            payload, ctype = safe_get(url, robots)
            if len(payload) > 5_000_000 or "html" not in ctype.lower():
                raise ValueError("Respuesta demasiado grande o no HTML")
            parser = MainTextParser()
            parser.feed(payload.decode("utf-8", errors="replace"))
            title, lines = parser.result()
            if len(" ".join(lines)) < 300:
                raise ValueError("La página no entregó texto público suficiente")
            source_id = upsert_source(conn, url, title or url, "web_html", url,
                                      "verified_public", "Extracción automática de página pública")
            replace_passages(conn, source_id,
                             [(f"Bloque {i}", body) for i, body in enumerate(chunks(lines), 1)])
            report["updated"].append(url)
        except Exception as exc:
            report["errors"].append(f"{url}: {exc}")
    try:
        payload, ctype = safe_get(REGULATION_URL, robots)
        if len(payload) > 5_000_000 or not payload.startswith(b"%PDF"):
            raise ValueError("PDF inválido o mayor de 5 MB")
        pdf_path = ASSETS / "reglamento-estudiantes-2026.pdf"
        pdf_path.write_bytes(payload)
        from pypdf import PdfReader
        reader = PdfReader(pdf_path)
        source_id = upsert_source(conn, REGULATION_URL, "Reglamento General de Estudiantes",
                                  "official_pdf", REGULATION_URL, "verified_public",
                                  f"{len(reader.pages)} páginas; extracción de texto por página")
        entries = []
        for page_number, page in enumerate(reader.pages, 1):
            page_text = page.extract_text() or ""
            entries.extend((f"Página {page_number}", block)
                           for block in chunks(page_text.splitlines()))
        replace_passages(conn, source_id, entries)
        report["updated"].append(REGULATION_URL)
    except Exception as exc:
        report["errors"].append(f"{REGULATION_URL}: {exc}")
    return report


STOP = {"como", "donde", "cual", "cuales", "para", "tiene", "tener", "puedo", "necesito",
        "esta", "estan", "sobre", "quiero", "informacion", "cesa", "nido", "hacer", "hago",
        "cuanto", "cuantos", "cuando", "acerca", "hay", "son", "una", "unos", "con", "del",
        "las", "los", "que", "por", "mis", "sus", "una", "en", "de", "el", "la", "y", "a",
        "ofrece", "ofrecer", "apoyo", "apoyos"}


def terms(value: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", normalize(value))
            if len(w) > 2 and w not in STOP}


def private_question(value: str) -> bool:
    q = normalize(value)
    patterns = (
        r"\b(mi|mis)\s+(nota|notas|calificacion|calificaciones|saldo|saldos|horario|correo)\b",
        r"\b(mis|las)\s+materias\s+(matriculadas|inscritas)\b",
        r"\b(que|cuales)\s+materias\s+(tengo|llevo)\b",
        r"\b(cuantas|cuantos)\s+(faltas|inasistencias)\s+(llevo|tengo)\b",
        r"\b(veo|consulto|mirar|ver)\s+mis\s+(faltas|inasistencias)\b",
        r"\b(me|mi)\s+(aprobaron|aprobaran|aprobarian)\s+(la\s+)?beca\b",
        r"\b(mi|mis)\s+beca\s+(esta|fue|ha sido)\s+aprobada\b",
        r"\b(cuanto|cuantos)\s+debo\s+(de\s+)?matricula\b",
    )
    if any(re.search(pattern, q) for pattern in patterns):
        return True
    return ("mi matricula" in q and
            not any(word in q for word in ("financiar", "financiacion", "credito", "beca")))


def routed_fact(q: str) -> str | None:
    """Conservative topic routing; a keyword alone never authorizes a new fact."""
    if ("certific" in q or "constancia" in q):
        if any(w in q for w in ("fisico", "impreso", "impresa", "papel")):
            return "certificate_physical"
        if (re.search(r"\b(graduad[oa]s?|gradue)\b", q)
                or ("egresado" in q and "titulo" in q)):
            return "certificate_graduates"
        return "certificate"
    if ("diploma" in q or "acta" in q) and any(w in q for w in ("copia", "duplicado", "solicito")):
        return "diploma_copy"
    if "nido" in q and any(w in q for w in ("entro", "entrar", "ingresar", "enlace", "link", "acceso", "portal")):
        return "nido_access"
    if any(w in q for w in ("incapacidad", "excusa", "justificar", "justificacion", "reprogramar")):
        return "medical"
    if any(w in q for w in ("inasistencia", "faltas", "falta a clase", "falto a")):
        return "attendance"
    if "saber pro" in q:
        if any(w in q for w in ("2025", "resultado", "quedo", "puesto", "ranking")):
            return "saber_news"
        return "saber_requirement"
    if "reglamento" in q and any(w in q for w in ("vigencia", "vigente", "rige", "desde cuando", "anterior", "2026", "2025")):
        return "regulation_effective"
    if "diga" in q or ("asesoria" in q and "escritura" in q):
        return "diga"
    if ("suma" in q and "centro" in q) or ("tutoria" in q and any(w in q for w in ("estadistica", "matematica", "numerica"))):
        return "suma"
    if "laboratorio financiero" in q:
        return "financial_lab"
    if "biblioteca" in q and any(w in q for w in ("servicios", "prestamo", "ebooks", "bases de datos")):
        return "library_services"
    if any(w in q for w in ("psicolog", "consejer", "estres", "salud mental", "emocional")):
        return "counseling"
    if "2026-2" in q and any(w in q for w in ("clase", "examen", "retir", "comenz", "empez")):
        if "retir" in q:
            return "calendar_withdraw_2026_2"
        if "examen" in q or "finales" in q:
            return "calendar_finals_2026_2"
        if "ultimo" in q or "termin" in q:
            return "calendar_last_2026_2"
        return "calendar_start_2026_2"
    if "icetex" in q:
        return "icetex"
    if ("beca" in q and "talento" in q) or ("fundacion bolivar" in q):
        return "talent_scholarship"
    if (any(w in q for w in ("beca", "financiacion", "financiar", "apoyo economico", "credito educativo"))
            or ("ayuda" in q and "financier" in q)):
        return "financial_aid"
    if "fiamma" in q or ("pizza" in q and "maquina" in q):
        return "pizza"
    if "encuesta" in q and "movilidad" in q:
        return "mobility"
    return None


def course_answer(query: str):
    q = normalize(query)
    if any(w in q for w in ("beca", "icetex", "financiacion", "financiar", "credito educativo", "retirar", "retiro")):
        return None
    if not any(w in q for w in ("malla", "materia", "asignatura", "semestre", "credito", "pensum", "plan de estudio", "practica")):
        return None
    if "credito" in q and any(word in q for word in ("total", "carrera", "programa", "malla", "pensum")):
        answer = "La malla aportada tiene 175 créditos distribuidos en nueve semestres: " + ", ".join(
            f"{i}: {credit}" for i, credit in enumerate(EXPECTED_CREDITS, 1)) + "."
        return answer
    if any(word in q for word in ("malla", "pensum", "plan de estudio")) and "semestre" not in q and not re.search(r"\b[1-9]\b", q):
        return "La malla aportada tiene nueve semestres y 175 créditos. Puedo detallar las materias y créditos de cada semestre; indica cuál quieres consultar."
    semester = None
    ordinal = {"primer": 1, "primero": 1, "segundo": 2, "tercer": 3, "tercero": 3,
               "cuarto": 4, "quinto": 5, "sexto": 6, "septimo": 7,
               "octavo": 8, "noveno": 9}
    for word, number in ordinal.items():
        if re.search(r"\b" + word + r"\b", q):
            semester = number
            break
    if semester is None:
        match = re.search(r"\b(?:semestre|sem|nivel)\s*([1-9])\b|\b([1-9])\s*(?:semestre|sem)\b", q)
        if match:
            semester = int(match.group(1) or match.group(2))
    if semester:
        courses = COURSES[semester]
        return (f"Semestre {semester} ({EXPECTED_CREDITS[semester-1]} créditos): " +
                "; ".join(f"{name} ({credit})" for name, credit in courses) + ".")
    scored = []
    q_terms = terms(q)
    for sem, courses in COURSES.items():
        for name, credit in courses:
            overlap = len(q_terms & terms(name))
            if overlap >= 2 or (len(q_terms) == 1 and overlap == 1 and len(next(iter(q_terms))) >= 6):
                scored.append((overlap, sem, name, credit))
    if scored:
        scored.sort(reverse=True)
        _, sem, name, credit = scored[0]
        return f"{name} figura en el semestre {sem} de la malla aportada y tiene {credit} créditos."
    return None


def search(question: str, conn: sqlite3.Connection) -> dict:
    q = " ".join(question.split())[:350]
    if len(q) < 3:
        return {"answer": "Escribe una pregunta más concreta.", "status": "no_match", "sources": []}
    normalized = normalize(q)
    if private_question(normalized):
        return {"answer": "No tengo acceso a tus notas, calificaciones ni saldos personales, y no hay una ruta privada de Nido verificada en esta base para consultarlos. Entra a Nido con tu cuenta institucional o consulta a Registro y Control.",
                "status": "no_match", "sources": []}
    if ("certific" in normalized and any(w in normalized for w in ("exactamente", "cuanto tarda", "cuanto demora", "plazo exacto", "en ingles"))):
        return {"answer": "No tengo un plazo exacto ni una confirmación sobre idioma de expedición para ese certificado en la fuente incorporada. Consulta a Registro y Control.",
                "status": "no_match", "sources": [{"title": "CESA, Registro y Control", "url": "https://www.cesa.edu.co/registro-y-control/", "status": "verified_public"}]}
    if ("laboratorio financiero" in normalized and
            any(w in normalized for w in ("donde", "ubicacion", "ubicado", "piso", "queda"))):
        return {"answer": "No puedo confirmar la ubicación actual del Laboratorio Financiero. Un usuario reportó que ahora está en el cuarto piso de Innovación, pero la página institucional aún indica el segundo piso de la Biblioteca. Antes de desplazarte, confirma en laboratorio.financiero@cesa.edu.co. El horario publicado es de lunes a viernes, de 8:00 a. m. a 5:00 p. m.",
                "status": "user_supplied", "topic": "Centros de apoyo", "fact_id": "financial_lab_location_conflict",
                "sources": [{"title": "CESA, Centros de Apoyo (ubicación posiblemente desactualizada)",
                "url": "https://www.cesa.edu.co/experiencia-cesa/centros-de-apoyo/",
                "status": "verified_public"}]}
    # A relative-date question cannot be answered from the already indexed 2026 calendar.
    if ((re.search(r"\b(proximo|siguiente)\s+semestre\b", normalized)
            and any(w in normalized for w in ("comienza", "empieza", "inicio", "inicia", "fecha")))
            or ("2027-1" in normalized and any(w in normalized for w in ("comienza", "empieza", "inicio", "inicia", "fecha", "calendario", "publicaron")))):
        return {"answer": "No tengo una fecha verificada de inicio para el próximo semestre. El calendario público incorporado llega a 2026-2; consulta la página oficial para ver si ya publicaron el período siguiente.",
                "status": "no_match", "sources": [{"title": "CESA, Calendario académico de pregrado",
                "url": "https://www.cesa.edu.co/calendario-academico/calendario-academico-pregrado/",
                "status": "verified_public"}]}
    course = course_answer(q)
    if course:
        return {"answer": course + " Fuente: malla aportada por Luis (20-05-2025), sin enlace público verificado. Comprueba que aplique a tu cohorte.",
                "status": "user_supplied", "sources": [{"title": CURRICULUM_SOURCE,
                "url": "", "status": "user_supplied"}]}
    q_terms = terms(q)
    fact_route = routed_fact(normalized)
    if fact_route:
        row = conn.execute("""SELECT f.*,s.url FROM facts f JOIN sources s ON s.id=f.source_id
                              WHERE f.id=?""", (fact_route,)).fetchone()
        if row:
            link = "" if row["url"].startswith("user-note:") else row["url"]
            return {"answer": row["answer"], "status": row["status"], "topic": row["topic"],
                    "fact_id": row["id"],
                    "sources": [{"title": row["citation"], "url": link, "status": row["status"]}]}
    ranked = []
    for row in conn.execute("""SELECT f.*,s.url FROM facts f JOIN sources s ON s.id=f.source_id"""):
        if fact_route and row["id"] != fact_route:
            continue
        question_terms = terms(row["question"])
        alias_terms = terms(row["aliases"])
        overlap = q_terms & (question_terms | alias_terms)
        score = len(overlap) + len(q_terms & question_terms)
        if row["id"] == "saber_requirement" and "2025" in q:
            score -= 4
        if row["id"] == "saber_news" and ("2026" in q or "2027" in q):
            score -= 4
        if row["id"] == "financial_aid" and not any(
                word in normalized for word in ("beca", "financ", "credito", "icetex", "economica", "economico")):
            score = 0
        if row["id"] == "nido_access" and len(overlap) < 2 and "nido" not in normalized:
            score = 0
        if row["id"] == "nido_access" and "nido" in normalized and overlap:
            score += 2
        if len(overlap) < (1 if len(q_terms) <= 2 else 2):
            score = 0
        if not fact_route and (score < 4 or len(overlap) < max(2, (len(q_terms) + 1) // 2)):
            score = 0
        if score > 0:
            ranked.append((score, row))
    ranked.sort(key=lambda x: x[0], reverse=True)
    if ranked and ranked[0][0] >= 2:
        row = ranked[0][1]
        second = ranked[1][0] if len(ranked) > 1 else 0
        if second >= ranked[0][0] and ranked[1][1]["topic"] != row["topic"]:
            return {"answer": "Encontré dos temas posibles. ¿Te refieres a " +
                    row["question"] + " o a " + ranked[1][1]["question"] + "?",
                    "status": "ambiguous", "sources": []}
        url = row["url"]
        if url.startswith("user-note:"):
            url = ""
        return {"answer": row["answer"], "status": row["status"], "topic": row["topic"],
                "fact_id": row["id"],
                "sources": [{"title": row["citation"], "url": url, "status": row["status"]}]}
    # A lexical hit is a navigation hint, not evidence that the question was answered.
    searchable = sorted(q_terms, key=len, reverse=True)[:5]
    if searchable:
        fts_query = " OR ".join(f'"{word}"' for word in searchable)
        hits = conn.execute("""SELECT p.section,p.body,s.title,s.url,s.status,bm25(passage_search) AS rank
          FROM passage_search JOIN passages p ON p.id=passage_search.rowid
          JOIN sources s ON s.id=p.source_id WHERE passage_search MATCH ?
          ORDER BY rank LIMIT 8""", (fts_query,)).fetchall()
        selected = []
        for hit in hits:
            if len(q_terms & terms(hit["body"])) >= min(2, len(q_terms)):
                selected.append(hit)
            if len(selected) == 2:
                break
        if selected:
            sources = []
            for hit in selected:
                link = hit["url"]
                if link.endswith(".pdf") and hit["section"].startswith("Página "):
                    link += "#page=" + hit["section"].split()[-1]
                if not any(item["url"] == link for item in sources):
                    sources.append({"title": hit["title"] + " — " + hit["section"],
                                    "url": link, "status": hit["status"]})
            return {"answer": "No tengo información verificada suficiente para responder esta pregunta concreta. Encontré una fuente posiblemente relacionada, pero no confirmé que contenga la respuesta; consulta el enlace o formula una pregunta más específica.",
                    "status": "no_match", "sources": sources[:1]}
    return {"answer": "No tengo información verificada suficiente para responder eso. Puedo buscar dentro de las fuentes públicas incorporadas, pero no tengo acceso a tu sesión de Nido ni a sus pantallas privadas.",
            "status": "no_match", "sources": []}


class Handler(BaseHTTPRequestHandler):
    def send_json(self, value, code=200):
        raw = json.dumps(value, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/api/status":
            with closing(connect()) as conn:
                counts = {name: conn.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
                          for name in ("sources", "facts", "courses", "passages")}
            counts["openai_configured"] = bool(os.getenv("OPENAI_API_KEY"))
            counts["direct_public_fetch_enabled"] = os.getenv("ENABLE_DIRECT_CESA_FETCH") == "1"
            with closing(connect()) as conn:
                from smart import web_fetches_last_24h
                counts["public_fetches_last_24h"] = web_fetches_last_24h(conn)
            counts["apify_runtime_configured"] = (
                os.getenv("ENABLE_COMPOSIO_APIFY") == "1" and
                bool(os.getenv("COMPOSIO_API_KEY")) and bool(os.getenv("COMPOSIO_USER_ID")) and
                importlib.util.find_spec("composio") is not None
            )
            self.send_json(counts)
            return
        if path == "/":
            filename = HERE / "index.html"
            content_type = "text/html; charset=utf-8"
        elif path == "/assets/malla-curricular-2025.pdf":
            filename = ASSETS / "malla-curricular-2025.pdf"
            content_type = "application/pdf"
        else:
            self.send_error(404)
            return
        if not filename.exists():
            self.send_error(404)
            return
        payload = filename.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        if path not in {"/api/chat", "/api/refresh"}:
            self.send_error(404)
            return
        size = int(self.headers.get("Content-Length", 0))
        if size > 4096:
            self.send_json({"error": "Solicitud demasiado larga"}, 413)
            return
        try:
            data = json.loads(self.rfile.read(size) or b"{}")
        except (ValueError, UnicodeDecodeError):
            self.send_json({"error": "JSON inválido"}, 400)
            return
        if path == "/api/chat":
            from smart import answer_question
            with closing(connect()) as conn:
                self.send_json(answer_question(str(data.get("question", "")), conn))
        else:
            if not WEB_LOCK.acquire(blocking=False):
                self.send_json({"error": "Ya hay una actualización en curso"}, 409)
                return
            try:
                with closing(connect()) as conn:
                    self.send_json(refresh_web(conn))
            finally:
                WEB_LOCK.release()


def main():
    parser = argparse.ArgumentParser(description="Asistente local del CESA con fuentes")
    parser.add_argument("command", choices=["serve", "seed", "refresh", "refresh-one", "ask"])
    parser.add_argument("question", nargs="?")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    with closing(connect()) as conn:
        seed_local(conn)
        if args.command == "refresh":
            print(json.dumps(refresh_web(conn), ensure_ascii=False, indent=2))
        elif args.command == "refresh-one":
            print(json.dumps(refresh_one_public_page(conn, args.question or ""), ensure_ascii=False, indent=2))
        elif args.command == "ask":
            from smart import answer_question
            print(json.dumps(answer_question(args.question or "", conn), ensure_ascii=False, indent=2))
        elif args.command == "seed":
            print(f"Base lista: {DB_PATH}")
    if args.command == "serve":
        server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
        print(f"Abre http://127.0.0.1:{args.port}/")
        print("Ctrl+C para detener. El servidor solo escucha en localhost.")
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            server.server_close()


if __name__ == "__main__":
    main()
