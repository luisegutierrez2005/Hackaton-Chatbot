import json
import tempfile
import threading
import unittest
import urllib.request
from contextlib import closing
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch

import app
import smart
import telegram_bridge
from knowledge import COURSES, EXPECTED_CREDITS
from simulacion_50 import CASES, EXPECTED_FACTS
from evaluar_simulacion import assess


class KnowledgeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.TemporaryDirectory()
        cls.db = Path(cls.tmp.name) / "test.sqlite3"
        cls.old_db = app.DB_PATH
        cls.old_assets = app.ASSETS
        cls.old_pdf = app.SOURCE_PDF
        app.DB_PATH = cls.db
        app.ASSETS = Path(cls.tmp.name) / "assets"
        app.SOURCE_PDF = Path(cls.tmp.name) / "missing.pdf"
        with closing(app.connect()) as conn:
            app.seed_local(conn)

    @classmethod
    def tearDownClass(cls):
        app.DB_PATH, app.ASSETS, app.SOURCE_PDF = cls.old_db, cls.old_assets, cls.old_pdf
        cls.tmp.cleanup()

    def ask(self, q):
        with closing(app.connect()) as conn:
            return app.search(q, conn)

    def test_curriculum_sums(self):
        self.assertEqual([sum(c for _, c in COURSES[s]) for s in range(1, 10)], EXPECTED_CREDITS)
        self.assertEqual(sum(EXPECTED_CREDITS), 175)

    def test_certificate_has_official_link(self):
        result = self.ask("Cómo pido un certificado en Nido")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("Autoservicio", result["answer"])
        self.assertIn("registro-y-control", result["sources"][0]["url"])

    def test_graduate_certificate_has_distinct_route(self):
        result = self.ask("¿Cómo solicito un certificado si ya me gradué?")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("juan.garciaa@cesa.edu.co", result["answer"])
        self.assertIn("comprobante", result["answer"])

    def test_psychology_not_confused_with_financial_aid(self):
        result = self.ask("¿Qué apoyo psicológico ofrece el CESA?")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("consejeria@cesa.edu.co", result["answer"])
        self.assertIn("bienestar/psicologia", result["sources"][0]["url"])

    def test_diga_location_and_booking(self):
        result = self.ask("¿Dónde queda el Centro DIGA y cómo pido una cita?")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("segundo piso", result["answer"])
        self.assertIn("centros-de-apoyo", result["sources"][0]["url"])

    def test_next_semester_date_abstains_with_calendar_link(self):
        result = self.ask("¿Cuándo comienza el próximo semestre de pregrado?")
        self.assertEqual(result["status"], "no_match")
        self.assertIn("calendario-academico-pregrado", result["sources"][0]["url"])

    def test_medical_five_percent_is_inclusive(self):
        result = self.ask("incapacidad médica examen 5%")
        self.assertIn("5 % o más", result["answer"])

    def test_unsupported_nido_route_abstains(self):
        result = self.ask("¿Dónde veo mi nota de cálculo en Nido?")
        self.assertEqual(result["status"], "no_match")

    def test_nido_access_plain_language(self):
        result = self.ask("Dónde entro a Nido")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("elluciancloud", result["sources"][0]["url"])

    def test_unverified_notice_marked(self):
        result = self.ask("Dónde está la máquina de pizzas Fiamma")
        self.assertEqual(result["status"], "user_supplied")

    def test_financial_aid_official(self):
        result = self.ask("Que ayudas financieras hay")
        self.assertEqual(result["status"], "verified_public")
        self.assertIn("Beca Crédito", result["answer"])

    def test_no_arbitrary_scrape(self):
        with self.assertRaises(ValueError):
            app.safe_get("https://experience.elluciancloud.com/cdesdac/")

    def test_one_page_refresh_rejects_nido_before_network(self):
        with closing(app.connect()) as conn:
            with self.assertRaises(ValueError):
                app.refresh_one_public_page(conn, "https://experience.elluciancloud.com/cdesdac/")

    def test_candidate_url_requires_unambiguous_public_match(self):
        urls = ["https://www.cesa.edu.co/biblioteca/reserva-salas/",
                "https://www.cesa.edu.co/financiacion-becas/"]
        self.assertEqual(smart.candidate_url("reserva de salas biblioteca", urls), urls[0])
        self.assertIsNone(smart.candidate_url("reserva de salas biblioteca", [
            "https://evil.example/biblioteca/reserva-salas/"]))

    def test_sitemap_discovery_ignores_external_urls(self):
        xml = b'''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        <url><loc>https://www.cesa.edu.co/biblioteca/reserva-salas/</loc></url>
        <url><loc>https://evil.example/biblioteca/reserva-salas/</loc></url>
        </urlset>'''
        urls = smart.sitemap_urls(fetch=lambda _: xml)
        self.assertEqual(urls, ["https://www.cesa.edu.co/biblioteca/reserva-salas/"])

    def test_private_question_never_uses_model_or_scraper(self):
        with closing(app.connect()) as conn:
            result = smart.answer_question("¿Cuál es mi horario?", conn,
                llm=lambda *_: self.fail("No debe llamarse el modelo"),
                scraper=object())
        self.assertEqual(result["status"], "no_match")
        self.assertIn("No tengo acceso", result["answer"])

    def test_personal_scholarship_and_absences_also_abstain(self):
        with closing(app.connect()) as conn:
            for question in ("¿Mi beca está aprobada?", "¿Cuántas faltas llevo en Matemáticas?"):
                with self.subTest(question=question):
                    result = smart.answer_question(question, conn,
                        llm=lambda *_: self.fail("No debe llamarse el modelo"),
                        scraper=object())
                    self.assertEqual(result["status"], "no_match")

    def test_general_financing_is_not_mistaken_for_private_balance(self):
        result = self.ask("¿Cómo puedo financiar mi matrícula?")
        self.assertEqual(result["status"], "verified_public")
        self.assertEqual(result["fact_id"], "financial_aid")

    def test_financial_lab_location_conflict_is_not_presented_as_verified(self):
        hours = self.ask("¿Cuál es el horario del Laboratorio Financiero?")
        self.assertEqual(hours["status"], "verified_public")
        self.assertNotIn("segundo piso", hours["answer"].lower())
        location = self.ask("¿Dónde queda el Laboratorio Financiero?")
        self.assertEqual(location["status"], "user_supplied")
        self.assertIn("cuarto piso de Innovación", location["answer"])
        self.assertIn("aún indica el segundo piso", location["answer"])

    def test_model_answer_from_sqlite_passage(self):
        with closing(app.connect()) as conn:
            source = app.upsert_source(conn, "https://www.cesa.edu.co/biblioteca/",
                "Biblioteca CESA", "web_html", "CESA", "verified_public")
            app.replace_passages(conn, source, [("Página", "La biblioteca dispone de salas de estudio y préstamo de libros para estudiantes. ")])
            result = smart.answer_question("¿Qué salas tiene la biblioteca?", conn,
                llm=lambda q, context: "Ofrece salas de estudio y préstamo de libros [1].")
        self.assertEqual(result["status"], "ai_draft")
        self.assertEqual(result["sources"][0]["url"], "https://www.cesa.edu.co/biblioteca/")

    def test_curated_fact_is_tailored_when_model_available(self):
        with closing(app.connect()) as conn:
            result = smart.answer_question("¿Cómo pido un certificado?", conn,
                llm=lambda q, context: "En Nido: Autoservicio → Solicitud de servicio → Certificados [1].")
        self.assertEqual(result["status"], "ai_draft")
        self.assertIn("registro-y-control", result["sources"][0]["url"])

    def test_scrape_on_miss_persists_one_public_page(self):
        class FakeScraper:
            def fetch(self, url):
                return {"url": url, "title": "Cabinas multimedia - CESA",
                        "markdown": ("La biblioteca del CESA permite reservar cabinas multimedia. " * 12)}

        class FakeRobots:
            def set_url(self, *_): pass
            def read(self): pass
            def can_fetch(self, *_): return True

        url = "https://www.cesa.edu.co/biblioteca/reserva-cabinas-multimedia/"
        with patch.dict("os.environ", {"ENABLE_COMPOSIO_APIFY": "1"}), \
                patch.object(smart.urllib.robotparser, "RobotFileParser", FakeRobots):
            smart.LAST_SCRAPE = 0.0
            with closing(app.connect()) as conn:
                conn.execute("DELETE FROM web_fetches")
                conn.commit()
                result = smart.answer_question("¿Cómo reservar cabinas multimedia?", conn,
                    llm=lambda q, context: "La biblioteca permite reservar cabinas multimedia [1].",
                    scraper=FakeScraper(), url_finder=lambda _: url)
                stored = conn.execute("SELECT COUNT(*) FROM passages p JOIN sources s ON s.id=p.source_id WHERE s.url=?", (url,)).fetchone()[0]
        self.assertGreater(stored, 0)
        self.assertEqual(result["status"], "ai_draft")
        self.assertEqual(result["sources"][0]["url"], url)

    def test_direct_public_fallback_fetches_one_page_with_budget(self):
        class FakeRobots:
            def set_url(self, *_): pass
            def read(self): pass
            def can_fetch(self, *_): return True

        url = "https://www.cesa.edu.co/biblioteca/impresion-3d/"
        with patch.dict("os.environ", {"ENABLE_DIRECT_CESA_FETCH": "1", "ENABLE_COMPOSIO_APIFY": "0"}), \
                patch.object(smart.urllib.robotparser, "RobotFileParser", FakeRobots), \
                patch.object(app, "store_one_public_page", return_value={"updated": url, "passages": 1}) as fetch:
            smart.LAST_SCRAPE = 0.0
            with closing(app.connect()) as conn:
                conn.execute("DELETE FROM web_fetches")
                conn.commit()
                result = smart.answer_question("¿Hay impresoras 3D en biblioteca?", conn,
                    url_finder=lambda _: url)
                count = conn.execute("SELECT COUNT(*) FROM web_fetches").fetchone()[0]
        self.assertEqual(fetch.call_count, 1)
        self.assertEqual(count, 1)
        self.assertEqual(result["status"], "no_match")
        self.assertIn("indexó una página", result.get("note", ""))

    def test_direct_fallback_stops_at_persistent_six_page_limit(self):
        url = "https://www.cesa.edu.co/biblioteca/nueva-pagina-publica/"
        with patch.dict("os.environ", {"ENABLE_DIRECT_CESA_FETCH": "1", "ENABLE_COMPOSIO_APIFY": "0"}), \
                patch.object(smart.urllib.robotparser, "RobotFileParser") as robots:
            smart.LAST_SCRAPE = 0.0
            with closing(app.connect()) as conn:
                conn.execute("DELETE FROM web_fetches")
                conn.executemany("INSERT INTO web_fetches(url,fetched_at) VALUES (?,?)",
                                 [(f"test-budget-{i}", app.now()) for i in range(6)])
                conn.commit()
                result = smart.answer_question("¿Hay una nueva página de biblioteca?", conn,
                    url_finder=lambda _: url)
                conn.execute("DELETE FROM web_fetches WHERE url LIKE 'test-budget-%'")
                conn.commit()
        self.assertEqual(result["status"], "no_match")
        self.assertIn("seis páginas", result.get("note", ""))
        robots.assert_not_called()

    def test_direct_fallback_cooldown_survives_process_restart(self):
        url = "https://www.cesa.edu.co/biblioteca/otra-pagina-publica/"
        with patch.dict("os.environ", {"ENABLE_DIRECT_CESA_FETCH": "1", "ENABLE_COMPOSIO_APIFY": "0"}), \
                patch.object(smart.urllib.robotparser, "RobotFileParser") as robots:
            smart.LAST_SCRAPE = 0.0
            with closing(app.connect()) as conn:
                conn.execute("DELETE FROM web_fetches")
                conn.execute("INSERT INTO web_fetches(url,fetched_at) VALUES (?,?)",
                             ("https://www.cesa.edu.co/biblioteca/primera/", app.now()))
                conn.commit()
                result = smart.answer_question("¿Hay otra página de biblioteca?", conn,
                    url_finder=lambda _: url)
        self.assertEqual(result["status"], "no_match")
        self.assertIn("temporalmente limitada", result.get("note", ""))
        robots.assert_not_called()

    def test_simulated_50_status_and_links(self):
        with patch.dict("os.environ", {"ENABLE_DIRECT_CESA_FETCH": "0", "ENABLE_COMPOSIO_APIFY": "0"}):
            with closing(app.connect()) as conn:
                for identifier, _, question, status, url in CASES:
                    with self.subTest(case=identifier):
                        result = smart.answer_question(question, conn)
                        passed, _, _ = assess(status, url, result, EXPECTED_FACTS.get(identifier))
                        self.assertTrue(passed, result)

    def test_uncited_model_output_is_not_shown_as_answer(self):
        with closing(app.connect()) as conn:
            result = smart.answer_question("¿Qué salas tiene la biblioteca?", conn,
                llm=lambda *_: "La biblioteca ofrece cualquier servicio imaginable.")
        self.assertNotEqual(result["status"], "ai_draft")
        self.assertIn("no incluyó citas", result["note"])

    def test_telegram_reply_includes_source_without_credentials(self):
        result = {"answer": "Dato", "status": "verified_public", "sources": [
            {"url": "https://www.cesa.edu.co/registro-y-control/"}]}
        reply = telegram_bridge.format_reply(result)
        self.assertIn("Dato", reply)
        self.assertIn("https://www.cesa.edu.co/registro-y-control/", reply)

    def test_http_chat_end_to_end_offline(self):
        server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            request = urllib.request.Request(
                f"http://127.0.0.1:{server.server_port}/api/chat",
                data=json.dumps({"question": "¿Cómo pido un certificado?"}).encode(),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(request, timeout=5) as response:
                result = json.load(response)
            self.assertEqual(result["status"], "verified_public")
            self.assertIn("registro-y-control", result["sources"][0]["url"])
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=5)


if __name__ == "__main__":
    unittest.main()
