---
name: nidobot-cesa
description: Mantener y evaluar el chatbot informativo CESA de este repositorio; ampliar fuentes públicas curadas, revisar respuestas y probar el adaptador OpenClaw sin acceder a Nido personal.
---

# NidoBot CESA

Trabaja dentro de este repositorio. Antes de cambiar respuestas, lee `README.md`, `knowledge.py`, `app.py` y el caso pertinente en `test_app.py`. La fuente pública o el archivo aportado debe respaldar el dato exacto, no solo mencionar el tema.

- Distingue `verified_public`, `user_supplied`, `extracted_public` y `no_match`. La extracción sin revisión no equivale a una respuesta verificada.
- Si una fuente institucional contradice un reporte reciente del usuario, conserva ambos orígenes y abstente de confirmar el dato hasta verificarlo. El Laboratorio Financiero es un caso documentado de este conflicto.
- No utilices cuentas, cookies, credenciales ni contenido autenticado de Nido. La información privada del estudiante queda fuera del prototipo.
- Tras modificar una ficha, añade una prueba para la respuesta y otra para el caso de ausencia o conflicto pertinente; ejecuta `python -m unittest -q` y `python evaluar_simulacion.py`.
- Para el canal OpenClaw, conserva `openclaw-workspace/AGENTS.md` como instrucción del agente y `openclaw-cesa-lookup/` como herramienta estrecha. No amplíes permisos de shell, archivos o navegador para atender una pregunta.
- No incluyas `data/`, PDFs locales, respuestas individuales de encuestas, tokens ni configuración global de OpenClaw en commits o ejemplos.

La batería de 50 preguntas es simulada y no prueba precisión con estudiantes reales. Si se cambia el comportamiento, actualiza el informe y separa pruebas automatizadas de observaciones de Telegram.
