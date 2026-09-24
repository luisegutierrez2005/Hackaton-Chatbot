# Evidencia y alcance del proyecto

Fecha de corte: 24 de septiembre de 2026. Las cifras siguientes provienen de dos formularios aportados por el equipo, no de una muestra probabilística ni de registros administrativos del CESA. Se publican solo agregados.

## Estudiantes (n = 10)

- 8/10 dicen tener dudas al menos ocasionalmente sobre trámites, plataformas o procesos (3 varias veces por semana, 5 ocasionalmente).
- 7/10 indican que tardan desde el mismo día hasta más de dos días en obtener respuesta de CESA Contigo; 3/10, menos de una hora.
- 9/10 reportan haber perdido cupo en una materia o grupo por decisiones tardías o errores al armar horario. Es autorreporte de esta muestra, no una tasa institucional.
- 6/10 prefieren un canal en la plataforma web de la universidad y 4/10 WhatsApp.
- 6/10 responden «Sí, definitivamente» a sugerencias automáticas de horarios; 2/10 «Tal vez» y 2/10 no lo ven necesario.
- 8 estudiantes contestaron la pregunta abierta sobre desconfianza; las respuestas aluden a errores, falta de cobertura o respuestas genéricas. No se publican los textos individuales.

## CESA Contigo (n = 2)

- Ambas personas estimaron cerca de 200 consultas en una semana normal y que durante matrícula el volumen se duplica o más. Son estimaciones de informantes, no una medición operativa independiente; no deben sumarse automáticamente a 400 consultas semanales.
- Las dos identificaron consultas repetidas: cupos/cruces/requisitos y pagos/certificados/incapacidades.
- Calificaron la viabilidad de integrar un chatbot con la plataforma con 3/5; una señaló costo y la otra costo, posibles errores y seguridad de datos.
- Sobre colaborar con acceso a información o integraciones, una marcó «Poco probable» y la otra «Necesitaría evaluarlo más». No existe aprobación institucional para integrar Nido.

## Prototipo frente a visión

| Capacidad | Estado |
|---|---|
| Preguntas generales con fichas, SQLite y enlaces públicos | Implementada en servicio local |
| Bot de Telegram por agente aislado OpenClaw y `cesa_lookup` | Demostrado en consultas manuales documentadas; depende de procesos locales activos |
| Extracción acotada de una página pública ante falta de cobertura | Implementada; el texto extraído se guarda sin validarse automáticamente |
| Redacción desde el backend con OpenAI Responses | Código opcional; clave independiente no configurada en la última verificación |
| Apify mediante Composio | Código opcional; conexión del backend no verificada en vivo |
| Widget en web institucional | Propuesta; la web local es solo demostración |
| Acceso a Nido, datos personales, NRC y optimizador de horarios | Propuesta futura sujeta a autorización, API, seguridad y datos oficiales; no implementada |
| Matrícula automática o modificación de Banner/Nido | Fuera de alcance |

## Prueba interna

La batería de `simulacion_50.py` obtuvo 50/50 coincidencias automatizadas de estado y enlace después de iteraciones, con 30 respuestas basadas en páginas oficiales, 8 en material aportado por el equipo y 12 abstenciones. No es una prueba ciega ni mide exactitud con estudiantes reales. El conflicto de ubicación del Laboratorio Financiero mostró que un enlace institucional puede estar desactualizado: la respuesta actual expone el conflicto y pide confirmación.
