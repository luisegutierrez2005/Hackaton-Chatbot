# César CESA — prototipo y visión

Proyecto académico independiente; no es un servicio oficial del CESA ni tiene acceso a cuentas de estudiantes.

**Visión propuesta:** un asistente en la web institucional que responda dudas generales, guíe trámites y, si el CESA autoriza una integración futura con Nido y sus datos, ayude a explorar combinaciones de horario sin hacer la matrícula por el estudiante. Esa integración, el optimizador de NRC y el escalamiento automatizado a CESA Contigo **no están implementados** aquí.

**Prototipo demostrable:** búsqueda y respuesta sobre información general en SQLite, web local y un agente aislado de OpenClaw conectado a Telegram mediante `cesa_lookup`. Las respuestas usan fichas y enlaces; el sistema se abstiene ante datos personales o evidencia insuficiente. El rastreo acotado de páginas públicas existe, pero el contenido extraído no pasa automáticamente a ser una respuesta verificada. La conexión de OpenAI Responses y Composio/Apify del backend es opcional y no estaba configurada en la última verificación documentada.

Las encuestas originales y la presentación de partida no se publican: contienen respuestas individuales y afirmaciones que pertenecen a la visión, no al prototipo. El resumen agregado se encuentra en [docs/EVIDENCIA_Y_ALCANCE.md](docs/EVIDENCIA_Y_ALCANCE.md). La [presentación actualizada](presentacion/Cesar_CESA_vision_y_prototipo_v8.pptx) separa explícitamente la visión futura del prototipo.

Un chatbot de **recuperación con fuentes**, no un asistente conectado a la sesión personal de Nido. Su base SQLite integra la malla PDF aportada por Luis, fichas verificadas del reglamento y del sitio oficial, avisos aportados por Luis (marcados sin vigencia confirmada) y fragmentos de páginas públicas. El módulo opcional `smart.py` puede redactar con OpenAI Responses API y, ante ausencia de cobertura, extraer una página pública concreta mediante Apify/Composio. No usa API de Ellucian ni inventa rutas privadas. Sin credenciales externas conserva la respuesta local anterior.

Estado al 24-09-2026: el servidor principal responde desde fichas curadas y fuentes locales; **no** tiene una clave independiente de OpenAI API ni Apify/Composio activos. La batería de [50 preguntas simuladas](EVALUACION_50_2026-09-24.md) pasó sus comprobaciones de ruta y enlace, pero solo 30 recibieron respuesta desde páginas oficiales; 12 se abstuvieron y 8 dependen de material aportado por Luis. No confundir la prueba simulada con precisión en usuarios reales.

## Ejecutar

Con Python 3.10+ y `pypdf` instalado (`python -m pip install -r requirements.txt`):

```powershell
python app.py seed
python app.py refresh
python app.py serve
```

Abrir `http://127.0.0.1:8765/`. El botón **Actualizar páginas públicas** repite la extracción. Si la red falla, la base existente permanece disponible. `pypdf` solo hace falta para indexar el texto completo del reglamento durante `refresh`; las fichas curadas y la malla funcionan sin él.

Para probar una única URL ya aprobada en `PUBLIC_PAGES`, sin recorrer el resto del sitio: `python app.py refresh-one "https://www.cesa.edu.co/experiencia-cesa/centros-de-apoyo/"`. Este camino usa Python/HTTPS directamente; no es una prueba de Apify ni Composio.

Existe un fallback directo para preguntas sin cobertura: `ENABLE_DIRECT_CESA_FETCH=1`. Solo elige una URL pública inequívoca del sitemap del CESA, verifica `robots.txt`, guarda una página por consulta, limita una consulta nueva cada diez minutos y seis en 24 horas. El texto recién extraído queda como `extracted_public`, **no** como respuesta ya verificada. Luis autorizó su activación y el servidor principal lo tiene encendido; `/api/status` expone `direct_public_fetch_enabled` y `public_fetches_last_24h`. Se verificó con una consulta a una noticia pública del Laboratorio de Futuro. No hay rastreo de Nido ni sesión autenticada.

Opcional: si cuentas con la malla PDF aportada durante el proyecto, cópiala a `assets/malla-source.pdf` antes de ejecutar `seed`, o define `CESA_MALLA_PDF` con su ruta local. El archivo no está en este repositorio público. Las materias transcritas son material de trabajo y deben contrastarse con la versión vigente para cada cohorte.

Prueba rápida sin navegador: `python app.py ask "¿Cómo pido un certificado?"`.

## Respuesta con IA y extracción bajo demanda

Configura **en el entorno local**, nunca en el chat ni dentro del código, `OPENAI_API_KEY` (clave de proyecto de OpenAI API). Opcionalmente `OPENAI_MODEL` selecciona el modelo; el valor predeterminado del prototipo es `gpt-6-luna`, cuya disponibilidad debe confirmarse en tu proyecto. Cuando existe una clave, la API redacta una respuesta específica con una ficha curada o pasajes recuperados como evidencia; exige referencias numéricas válidas. Sin clave, las fichas siguen siendo respuestas locales directas. Se envía `store: false` y nunca se envían datos de Nido autenticado. Si falla la red o el modelo se abstiene, no se simula una respuesta generada.

Para activar extracción en una falta de cobertura, instala el SDK `composio` y configura `COMPOSIO_API_KEY`, `COMPOSIO_USER_ID` y `ENABLE_COMPOSIO_APIFY=1` en el **proceso que ejecuta `app.py`**. La conexión de Apify dentro de este chat no configura automáticamente ese proceso. No uses el identificador de usuario de otro proyecto sin verificar que corresponda a la conexión Apify de tu cuenta.

El orquestador lee un sitemap público, exige coincidencia inequívoca con una URL `https://www.cesa.edu.co/`, comprueba `robots.txt` y llama al actor `apify/website-content-crawler` para **una sola página**, profundidad 0, sin cookies ni login, con tope por ejecución de USD 0,10 y espera de hasta 90 segundos. Guarda el texto y la URL en SQLite para consultas siguientes. Registra en SQLite el máximo de seis consultas en 24 horas y la espera de diez minutos entre consultas nuevas, incluso después de reiniciar el servidor; evita repetir una URL guardada en las últimas 24 horas. Estos controles de prototipo no sustituyen límites por usuario ni un presupuesto de cuenta. La respuesta generada se marca como borrador con fuente para comprobar; no es una validación factual automática.

Para probar: `python -m unittest -v`, `python evaluar_simulacion.py` o `python evaluar_simulacion.py --http` con el servidor local activo. Las pruebas usan dobles de las APIs; **no prueban** la conexión real a OpenAI ni a Composio/Apify. El servidor sigue limitado a localhost.

## Telegram: camino corto para el hackatón

En la instalación local usada para la demostración, Telegram se asoció a un agente aislado `cesa` de OpenClaw mediante `cesa_lookup`. Una copia del repositorio **no** queda conectada automáticamente a Telegram; consulta [docs/CONFIGURACION_OPENCLAW.md](docs/CONFIGURACION_OPENCLAW.md).

`telegram_bridge.py` consulta la misma base directamente por [long polling de Telegram](https://core.telegram.org/bots/api#getupdates). No expone el puerto local ni requiere OpenClaw. Crea un bot con BotFather y configura `TELEGRAM_BOT_TOKEN` **en el entorno local, nunca en este chat**; luego ejecuta `python telegram_bridge.py`. El proceso debe seguir encendido para responder. Solo procesa mensajes privados de texto. Por ejecución acepta hasta 50 preguntas globales y 10 por chat, con ocho segundos mínimos entre preguntas del mismo chat; se puede ajustar con `TELEGRAM_MAX_QUESTIONS` y `TELEGRAM_MAX_PER_CHAT`. Guarda únicamente el offset de Telegram, no el texto de las conversaciones.

El adaptador alternativo `telegram_bridge.py` solo se probó con respuestas simuladas. En el canal OpenClaw, Telegram y la herramienta `cesa_lookup` ya respondieron en pruebas manuales anteriores; la evaluación de 15 preguntas del 24-09-2026 se hizo contra `/api/chat`, no directamente contra Telegram.

Estado de la demostración local al 24-09-2026: con autorización del propietario, **solo la cuenta Telegram `cesa`** permite mensajes privados de cualquier usuario (`dmPolicy=open`, `allowFrom=["*"]`). El agente conserva el perfil de herramientas mínimo y `cesa_lookup` como única herramienta adicional; el gateway y el servicio local respondían en la última comprobación. Hubo una interrupción de sondeo de Telegram que se recuperó, y aún **no se verificó una respuesta completa desde la cuenta externa mostrada en la prueba del QR**. El QR no limita quién puede encontrar el bot: el acceso abierto puede generar consumo de API y requiere observar fallos, abuso y costos. No publiques tu agente general con acceso a archivos o shell.

## Alcance y procedencia

- **Páginas públicas:** el actualizador completo lee `robots.txt`, consulta trece URL fijas de `www.cesa.edu.co` y el PDF oficial del reglamento. La consulta bajo demanda solo elige una URL inequívoca del sitemap y aplica los límites indicados arriba. No hace búsquedas con `?s=`, no toca Nido ni salta inicios de sesión. Para ampliar cobertura curada, revisar y agregar URL públicas a `PUBLIC_PAGES` en `knowledge.py`.
- **Malla:** copia local de la página única suministrada por Luis (`assets/malla-curricular-2025.pdf`). Materias y créditos se transcribieron para búsqueda estructurada; los totales de los nueve semestres coinciden con los impresos (175 créditos). La versión aplicable a cada cohorte debe confirmarse con Registro y Control.
- **Reglamento:** respuestas clave ancladas en artículos y página del PDF oficial. Para preguntas no cubiertas por fichas, se presentan fragmentos de texto con enlace y se advierte que no equivalen a una respuesta completa validada.
- **Avisos:** Pizza Fiamma y encuesta provienen del texto de Luis. No hay confirmación pública de horarios, vigencia o administración del formulario.
- **Saber Pro:** la cifra de 182 y el primer lugar **en Administración** están respaldados por una noticia oficial del CESA del 9 de septiembre de 2026; no se presentan como primer lugar nacional global.

## Limitaciones importantes

La extracción web cubre un subconjunto, no todo `cesa.edu.co`, y una coincidencia textual puede carecer del contexto necesario. Antes de usarlo para decisiones académicas hay que probar preguntas reales, revisar rutas en Nido con una cuenta autorizada sin copiar datos personales, y mantener fuentes/versiones. El servidor solo escucha en `127.0.0.1`; no tiene autenticación y no debe exponerse a Internet tal como está.

El proyecto de hackatón está aislado y no tiene relación con el futuro reto Avianca.

## Estructura publicable

- `app.py`, `smart.py`, `knowledge.py`: servicio local, búsqueda y fichas.
- `openclaw-cesa-lookup/`: herramienta `cesa_lookup` para el agente de OpenClaw.
- `openclaw-workspace/AGENTS.md`: instrucciones operativas y límites del agente César.
- `openclaw-workspace/IDENTITY.md` y `SOUL.md`: nombre, voz y límites de César.
- `openclaw-workspace/skills/`: tres skills del agente para trámites públicos, información académica general y apoyo estudiantil no clínico. Son instrucciones, no integraciones nuevas ni permisos.
- `presentacion/Cesar_CESA_vision_y_prototipo_v8.pptx`: presentación editable basada en la V7, con el estado actual del prototipo y la validación externa pendiente.
- `skills/nidobot-cesa/SKILL.md`: guía de mantenimiento y evaluación del proyecto.
- `test_app.py`, `evaluar_simulacion.py`: pruebas reproducibles. El conjunto de 50 preguntas es simulado, no una prueba de precisión con usuarios reales.

No se incluyen tokens, bases SQLite, respuestas crudas de encuestas, documentos locales ni la configuración global de OpenClaw. El servidor escucha solo en `127.0.0.1`; no se debe exponer a Internet sin autenticación, límites por usuario y una revisión de seguridad. No se incluye licencia de reutilización.
