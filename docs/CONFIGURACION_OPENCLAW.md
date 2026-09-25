# Ejecutar con OpenClaw y Telegram

Esta guía describe una instalación nueva. No copia la configuración ni las credenciales de la demostración local. Comprueba la sintaxis con `openclaw --help` en la versión instalada; OpenClaw puede cambiar comandos y claves de configuración.

## Servicio de datos

En el directorio raíz del repositorio:

```powershell
python -m pip install -r requirements.txt
python app.py seed
python app.py refresh
python app.py serve
```

Comprueba `http://127.0.0.1:8765/api/status` y una pregunta con `python app.py ask "¿Cómo pido un certificado de estudios?"`. `refresh` consulta fuentes públicas del CESA; revisa sus URL y condiciones antes de ejecutarlo. `serve` solo escucha en localhost.

## Herramienta del agente

En otra terminal, dentro de `openclaw-cesa-lookup/`:

```powershell
npm ci
npm run build
npm test
openclaw plugins validate --entry ./dist/index.js
```

Instala o enlaza el complemento con el procedimiento que indique tu versión de OpenClaw. Crea un agente **separado** cuyo workspace sea `openclaw-workspace/`, con `AGENTS.md`, `IDENTITY.md`, `SOUL.md` y sus tres skills en `skills/`. Si tu instalación ya usa otra ruta para el agente CESA, copia únicamente esos archivos públicos tras revisar qué hay allí; no sustituyas su estado ni sus credenciales sin comprobarlo. El conjunto de herramientas del agente no debe permitir más que `cesa_lookup` y las capacidades mínimas del canal. Los archivos de personalidad y las skills **no** conceden permisos. El plugin solo llama a `127.0.0.1:8765`; no le des acceso a shell, archivos, navegador ni sesiones personales.

## Canal Telegram

Crea tu propio bot con BotFather y guarda el token solo en el almacén local de secretos o la configuración privada de OpenClaw. No lo escribas en archivos del repositorio, commits, issues ni chats. Vincula la cuenta de Telegram al agente CESA aislado y conserva una política de emparejamiento o lista permitida durante las pruebas. Si se amplía el acceso a otras personas, revisa antes límites por usuario, costos del modelo y supervisión del contenido.

En la demostración local de César, el propietario autorizó el acceso abierto a mensajes privados **solo** para la cuenta `cesa`. Esta guía no publica ni copia esa configuración. Un acceso así admite a cualquiera que encuentre el usuario del bot, no solo a quien reciba el QR. La conexión del gateway se comprobó, pero la respuesta desde la cuenta externa usada en la prueba del QR sigue pendiente de confirmación.

La ruta directa `telegram_bridge.py` es alternativa, no un segundo proceso simultáneo: dos consumidores de `getUpdates` para el mismo bot pueden interferir. La web local llama directamente a `/api/chat` y no pasa por OpenClaw.

## Funciones que no se habilitan con estos pasos

No hay acceso a Nido autenticado, notas, pagos personales, NRC, motor de horarios ni matrícula automática. `OPENAI_API_KEY` y `COMPOSIO_API_KEY` son opciones independientes del backend, no son la sesión de ChatGPT ni se heredan de OpenClaw. El acceso abierto de la demostración no equivale a un servicio listo para producción: faltan validación externa, límites por usuario, control de costos, revisión de privacidad y observabilidad.
