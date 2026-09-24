"""Curated CESA facts. These are evidence records, not instructions to the bot."""

CURRICULUM_SOURCE = "Malla curricular completa ESPAÑOL, archivo aportado por Luis (20-05-2025), página 1"
REGULATION_URL = "https://www.cesa.edu.co/documents/731/Reglamento_general_de_estudiantes.pdf"
STUDENTS_URL = "https://www.cesa.edu.co/comunidad/estudiantes/"
REGISTRY_URL = "https://www.cesa.edu.co/registro-y-control/"
CENTERS_URL = "https://www.cesa.edu.co/experiencia-cesa/centros-de-apoyo/"
COUNSELING_URL = "https://www.cesa.edu.co/experiencia-cesa/bienestar/psicologia/"
CALENDAR_URL = "https://www.cesa.edu.co/calendario-academico/calendario-academico-pregrado/"
LIBRARY_SERVICES_URL = "https://www.cesa.edu.co/biblioteca/servicios-biblioteca/"
SABER_URL = "https://www.cesa.edu.co/news/administracion-empresas-saber-pro-2025-primer-lugar/"
NIDO_URL = "https://experience.elluciancloud.com/cdesdac/"

# Course names and credit values were transcribed from the supplied single-page PDF.
# The PDF remains attached in the app for comparison. This is not enrollment advice.
COURSES = {
    1: [("Matemáticas Aplicadas 1", 4), ("Comunicación Escrita", 3), ("Introducción a la Economía", 3), ("Historia Empresarial", 2), ("Fundamentos de Administración", 3), ("Contabilidad Básica", 3), ("Introducción al Derecho", 2), ("Bienestar 1", 0)],
    2: [("Matemáticas Aplicadas 2", 3), ("Comunicación Oral", 3), ("Microeconomía", 3), ("Pensamiento Administrativo", 2), ("Administración de Costos", 2), ("TIC Aplicadas a la Toma de Decisiones", 2), ("Derecho de Negocios", 2), ("Electiva Sociohumanística", 2), ("Bienestar 2", 0)],
    3: [("Estadística y Probabilidad", 3), ("Macroeconomía", 3), ("Principios de Mercadeo", 3), ("Planeación y Control Estratégico", 3), ("Análisis Financiero", 2), ("Creatividad e Innovación", 2), ("Derecho Laboral", 2), ("Electiva Sociohumanística", 2), ("Idiomas 1", 0), ("Grandes Líderes", 0), ("Bienestar 3", 0)],
    4: [("Estadística Aplicada", 3), ("Historia Económica", 2), ("Diseño Organizacional", 3), ("Matemáticas Financieras", 3), ("Gestión Humana", 3), ("Derecho Tributario", 2), ("Proyecto Integrador Espíritu Emprendedor", 4), ("Idiomas 2", 0), ("Bienestar 4", 0)],
    5: [("Investigación de Operaciones", 3), ("Coyuntura Económica", 3), ("Investigación de Mercados", 2), ("Transformación Personal", 2), ("Administración Financiera", 3), ("Comportamiento Organizacional", 3), ("Gestión para lo Público", 2), ("Electiva Sociohumanística", 2), ("Idiomas 3", 0), ("Bienestar 5", 0)],
    6: [("Visitas 1", 2), ("Administración de Operaciones", 3), ("Dirección Comercial", 2), ("Transformación Organizacional", 2), ("Negocios Internacionales", 2), ("Mercado de Capitales", 3), ("Gestión de Innovación", 2), ("Modelos para la Toma de Decisiones", 3), ("Idiomas 4", 0), ("Bienestar 6", 0)],
    7: [("Visitas 2", 3), ("Gerencia de la Cadena de Suministro", 3), ("Seminario Preparación para la Vida Laboral", 0), ("Marketing Digital", 2), ("Sostenibilidad Empresarial", 3), ("Planeación Financiera", 3), ("Electiva Profesional", 3), ("Proyecto Integrador Reto Empresarial", 4)],
    8: [("Práctica 1", 10), ("Dirección Estratégica de Mercadeo", 3), ("Electiva Profesional", 3), ("Seminario de Investigación", 2)],
    9: [("Práctica 2", 10), ("Requisito Inglés", 0), ("Liderazgo", 2), ("Electiva Profesional", 3), ("Trabajo de Grado", 3)],
}
EXPECTED_CREDITS = [20, 19, 20, 20, 20, 19, 21, 18, 18]

# Each record has a human-written answer constrained to a cited source.
# "user_supplied" means no official confirmation of current validity.
FACTS = [
    {
        "id": "nido_access", "question": "¿Dónde entro a Nido Académico?",
        "aliases": "entrar entro ingreso ingresar acceder acceso portal nido link enlace sistema academico",
        "answer": "Entra a Nido Académico desde el enlace del portal estudiantil del CESA. El acceso puede pedir autenticación institucional; este chatbot no tiene acceso a tu sesión ni a tus datos personales.",
        "url": NIDO_URL, "source": "CESA, Información para estudiantes", "support_url": STUDENTS_URL,
        "status": "verified_public", "topic": "Nido",
    },
    {
        "id": "certificate", "question": "¿Cómo solicito un certificado en Nido?",
        "aliases": "pedir solicitar certificado constancia certificacion estudio notas registro control",
        "answer": "Si eres estudiante activo o egresado no graduado: 1) entra a Nido Académico; 2) abre Autoservicio del estudiante → Solicitud de servicio; 3) selecciona la categoría Certificados y el tipo de certificado; 4) para pagar, ve a Resumen de cuenta por periodo → Ver saldos por tipo de documento. El CESA indica que el certificado se consulta en Nido dentro de los tiempos establecidos. El trámite para graduados comienza con una solicitud por correo y es distinto.",
        "url": REGISTRY_URL, "source": "CESA, Registro y Control, Solicitud de certificados", "status": "verified_public", "topic": "Nido y trámites",
    },
    {
        "id": "certificate_graduates", "question": "¿Cómo solicita un certificado una persona graduada?",
        "aliases": "graduado graduada gradué egresado título certificado certificación diploma",
        "answer": "Si ya te graduaste, el CESA indica que debes solicitar el certificado a juan.garciaa@cesa.edu.co, adjuntando copia del documento de identidad por ambas caras para validar la información y recibir credenciales de Nido. Con las credenciales, haces la solicitud y el pago en Nido; después envías el comprobante al mismo correo. El CESA indica que el certificado se envía por correo electrónico. No envíes tu documento ni otros datos personales a este chatbot.",
        "url": REGISTRY_URL, "source": "CESA, Registro y Control, Estudiantes graduados", "status": "verified_public", "topic": "Nido y trámites",
    },
    {
        "id": "certificate_physical", "question": "¿Cómo pido un certificado físico?",
        "aliases": "certificado constancia fisico impreso papel correo",
        "answer": "El CESA indica que los certificados se emiten digitalmente. Si lo necesitas en físico, notifícalo a juan.garciaa@cesa.edu.co. La página no publica aquí un plazo específico de entrega para certificados.",
        "url": REGISTRY_URL, "source": "CESA, Registro y Control, Solicitud de certificados", "status": "verified_public", "topic": "Nido y trámites",
    },
    {
        "id": "diploma_copy", "question": "¿Cómo solicito una copia del diploma o acta?",
        "aliases": "copia diploma acta duplicado titulo graduacion solicitud",
        "answer": "Para una copia de acta o diploma, el CESA indica escribir a juan.garciaa@cesa.edu.co con el programa de estudios y copia del documento de identidad por ambas caras. Tras la validación, entrega credenciales para solicitar en el autoservicio la categoría «Solicitudes académicas» y el servicio «Copia de acta / diploma», y continuar con el pago. La página publica un plazo estimado de 20 a 25 días hábiles para estos documentos. No envíes documentos personales a este chatbot.",
        "url": REGISTRY_URL, "source": "CESA, Registro y Control, Copias de acta y diplomas", "status": "verified_public", "topic": "Nido y trámites",
    },
    {
        "id": "attendance", "question": "¿Con cuántas inasistencias se pierde una materia?",
        "aliases": "faltas asistencia inasistencias 30 porcentaje materia perder cero reglamento",
        "answer": "Según el artículo 44 del Reglamento General de Estudiantes, si las inasistencias superan el 30 % de las clases programadas y dictadas, la calificación final de la asignatura es 0,0. El umbral es «superar» 30 %, no simplemente llegar a 30 %.",
        "url": REGULATION_URL + "#page=16", "source": "Reglamento General de Estudiantes, art. 44, p. 16", "status": "verified_public", "topic": "Reglamento",
    },
    {
        "id": "medical", "question": "¿Qué pasa con una incapacidad médica y una evaluación?",
        "aliases": "incapacidad medica excusa examen parcial actividad evaluativa 5 reprogramar faltas asistencia",
        "answer": "El artículo 45 indica que la justificación debe presentarse por el canal establecido dentro de los tres días calendario siguientes a la ausencia. Con una incapacidad médica validada pueden reprogramarse actividades evaluativas que representen el 5 % o más de la nota de la materia. La incapacidad validada no elimina la inasistencia registrada. Tras validar la excusa, el profesor reprograma la actividad; podría requerirse pagar los derechos correspondientes, si aplica.",
        "url": REGULATION_URL + "#page=17", "source": "Reglamento General de Estudiantes, art. 45, pp. 16–17", "status": "verified_public", "topic": "Reglamento",
    },
    {
        "id": "saber_requirement", "question": "¿Cuál es el requisito Saber Pro para graduarse?",
        "aliases": "saber pro 2026 2027 puntaje percentil nivelacion graduacion requisito",
        "answer": "El artículo 66 exige ubicarse al menos en el percentil 75 del puntaje global nacional y no estar por debajo del percentil 50 en las competencias evaluadas. Para quienes presenten Saber Pro en 2026 o 2027 y no cumplan, el reglamento contempla un plan de nivelación transitorio; consulta el artículo completo para sus condiciones.",
        "url": REGULATION_URL + "#page=23", "source": "Reglamento General de Estudiantes, art. 66, p. 23", "status": "verified_public", "topic": "Reglamento",
    },
    {
        "id": "regulation_effective", "question": "¿Desde cuándo rige el nuevo reglamento estudiantil?",
        "aliases": "vigencia reglamento 2026 2025 disciplinario transicion",
        "answer": "El Reglamento General de Estudiantes entró en vigencia el 11 de junio de 2026. Sus disposiciones académicas aplican a estudiantes antiguos y nuevos matriculados desde el período 2026-2. Los procesos disciplinarios derivados de faltas anteriores a su entrada en vigencia siguen bajo el procedimiento del reglamento de 2025.",
        "url": REGULATION_URL + "#page=34", "source": "Reglamento General de Estudiantes, arts. 96–99, p. 34", "status": "verified_public", "topic": "Reglamento",
    },
    {
        "id": "saber_news", "question": "¿Cómo le fue al CESA en Saber Pro 2025?",
        "aliases": "resultado saber pro 2025 primero administracion 182 puntos ranking",
        "answer": "El CESA informó el 9 de septiembre de 2026 que ocupó el primer lugar en el área de Administración en Saber Pro 2025, con promedio ponderado de 182 puntos en el puntaje global. Ese primer lugar es en Administración, no en el ranking general de todas las instituciones.",
        "url": SABER_URL, "source": "CESA, noticia publicada el 09-09-2026", "status": "verified_public", "topic": "Noticias",
    },
    {
        "id": "financial_aid", "question": "¿Qué becas y opciones de financiación ofrece el CESA?",
        "aliases": "ayudas financieras becas financiacion credito icetex descuentos oportunidades apoyo economico",
        "answer": "La página de Becas y financiación del CESA enumera: crédito ICETEX (hasta 100 % de la matrícula, sujeto a requisitos), convenios con instituciones financieras, línea de crédito directo con CESA, beca temporal y beca permanente (cada una hasta 50 %, sujetas a condiciones), posibles descuentos, y la Beca Crédito para el Talento CESA–Fundación Bolívar Davivienda. Esta última está dirigida a estudiantes de pregrado entre 4.º y 8.º semestre en riesgo de abandonar por barreras económicas; cubre 90 % de la matrícula (45 % beca condonable y 45 % crédito), y el estudiante paga el 10 % restante. Para requisitos completos y fechas vigentes, consulta la página oficial o escribe a becas@cesa.edu.co.",
        "url": "https://www.cesa.edu.co/financiacion-becas/", "source": "CESA, Becas y financiación, consultado el 23-09-2026", "status": "verified_public", "topic": "Apoyo financiero",
    },
    {
        "id": "counseling", "question": "¿Qué apoyo psicológico y consejería ofrece el CESA?",
        "aliases": "psicologia psicologico psicologica consejeria bienestar emocional estres crisis",
        "answer": "El CESA ofrece consejería privada y confidencial, atendida por psicólogas de la institución. La página menciona apoyo en adaptación, plan de estudios, riesgo académico, hábitos, estrés, emociones y contención en crisis. Para contactar el servicio: consejeria@cesa.edu.co o 3157534076. La página no describe un sistema de reservas; consulta al servicio cómo programar una atención.",
        "url": COUNSELING_URL, "source": "CESA, Bienestar, Apoyo psicológico y consejería", "status": "verified_public", "topic": "Bienestar",
    },
    {
        "id": "diga", "question": "¿Dónde está el Centro DIGA y cómo pido una cita?",
        "aliases": "centro diga asesorias comunicacion escritura oral cita biblioteca horario",
        "answer": "El Centro DIGA está en el segundo piso de la Biblioteca. Ofrece asesorías de comunicación escrita y oral. En la página oficial de Centros de Apoyo encontrarás el botón «Agenda una cita». Su horario publicado es de lunes a viernes, presencial o virtual de 8:00 a. m. a 5:00 p. m., y exclusivamente virtual de 5:00 p. m. a 7:00 p. m. También puedes escribir a diga@cesa.edu.co.",
        "url": CENTERS_URL, "source": "CESA, Centros de Apoyo, Centro DIGA", "status": "verified_public", "topic": "Centros de apoyo",
    },
    {
        "id": "suma", "question": "¿En qué me ayuda el Centro SUMA?",
        "aliases": "suma matematicas estadistica numericas asesorias tutorias nivelatorios",
        "answer": "El Centro SUMA apoya las habilidades numéricas y matemáticas de la comunidad CESA. La página oficial enumera asesorías y tutorías individuales o grupales, cursos nivelatorios, apoyo a trabajos de grado y medición de habilidades matemáticas. No encontré en esa página un horario propio del Centro SUMA.",
        "url": CENTERS_URL, "source": "CESA, Centros de Apoyo, Centro SUMA", "status": "verified_public", "topic": "Centros de apoyo",
    },
    {
        "id": "financial_lab", "question": "¿Cuál es el horario del Laboratorio Financiero?",
        "aliases": "laboratorio financiero bloomberg biblioteca horario asesorias",
          "answer": "El horario publicado del Laboratorio Financiero es de lunes a viernes de 8:00 a. m. a 5:00 p. m. Su correo publicado es laboratorio.financiero@cesa.edu.co. Ofrece asesoría para obtener información financiera y actividades de acercamiento con el sector financiero. La ubicación no se incluye porque hay una discrepancia entre la web institucional y una corrección reciente de un usuario.",
        "url": CENTERS_URL, "source": "CESA, Centros de Apoyo, Laboratorio Financiero", "status": "verified_public", "topic": "Centros de apoyo",
    },
    {
        "id": "calendar_start_2026_2", "question": "¿Cuándo empezaron las clases de 2026-2?",
        "aliases": "inicio comienzan empezaron clases semestre 2026-2 julio",
        "answer": "Según el calendario académico de pregrado del CESA, las clases del período 2026-2 comenzaron el 21 de julio de 2026.",
        "url": CALENDAR_URL, "source": "CESA, Calendario académico de pregrado 2026, inicio de clases", "status": "verified_public", "topic": "Calendario 2026-2",
    },
    {
        "id": "calendar_last_2026_2", "question": "¿Cuál es el último día de clase de 2026-2?",
        "aliases": "ultimo dia clases semestre 2026-2 noviembre",
        "answer": "El calendario académico de pregrado del CESA fija el último día de clase de 2026-2 para el 23 de noviembre de 2026.",
        "url": CALENDAR_URL, "source": "CESA, Calendario académico de pregrado 2026, último día de clase", "status": "verified_public", "topic": "Calendario 2026-2",
    },
    {
        "id": "calendar_finals_2026_2", "question": "¿Cuándo son los exámenes finales de 2026-2?",
        "aliases": "examenes finales pruebas semestre 2026-2 noviembre",
        "answer": "El calendario académico de pregrado del CESA programa los exámenes finales de 2026-2 del 17 al 21 de noviembre de 2026. La misma fila aclara que en esa semana no hay clases, solo exámenes programados.",
        "url": CALENDAR_URL, "source": "CESA, Calendario académico de pregrado 2026, exámenes finales", "status": "verified_public", "topic": "Calendario 2026-2",
    },
    {
        "id": "calendar_withdraw_2026_2", "question": "¿Hasta cuándo puedo retirar una asignatura en 2026-2?",
        "aliases": "retiro retirar asignatura materia semestre 2026-2 octubre",
        "answer": "El calendario académico de pregrado del CESA señala el 16 de octubre de 2026 como último día para retirar asignaturas en 2026-2.",
        "url": CALENDAR_URL, "source": "CESA, Calendario académico de pregrado 2026, retiro de asignaturas", "status": "verified_public", "topic": "Calendario 2026-2",
    },
    {
        "id": "icetex", "question": "¿ICETEX puede cubrir el 100 % de la matrícula?",
        "aliases": "icetex credito cien 100 porcentaje matricula pregrado posgrado",
        "answer": "La página de financiación del CESA indica que ICETEX puede financiar hasta el 100 % del valor de la matrícula en pregrado y posgrado, para estudiantes de cualquier semestre que cumplan los requisitos de ICETEX. No significa que todas las solicitudes sean aprobadas.",
        "url": "https://www.cesa.edu.co/financiacion-becas/", "source": "CESA, Becas y financiación, ICETEX", "status": "verified_public", "topic": "Apoyo financiero",
    },
    {
        "id": "talent_scholarship", "question": "¿A quién aplica la Beca Crédito para el Talento CESA?",
        "aliases": "beca credito talento fundacion bolivar davivienda cuarto octavo 4 8 semestre",
        "answer": "La Beca Crédito para el Talento CESA–Fundación Bolívar Davivienda está dirigida a estudiantes de pregrado entre cuarto y octavo semestre en riesgo de abandonar por barreras económicas, sujetos a los demás requisitos publicados por el CESA. Cubre el 90 % de la matrícula: 45 % beca condonable y 45 % crédito; el estudiante paga el 10 % restante. No puedo verificar si una persona concreta fue aprobada.",
        "url": "https://www.cesa.edu.co/financiacion-becas/", "source": "CESA, Becas y financiación, Beca Crédito para el Talento", "status": "verified_public", "topic": "Apoyo financiero",
    },
    {
        "id": "library_services", "question": "¿Qué servicios ofrece la Biblioteca CESA?",
        "aliases": "biblioteca servicios prestamo libros ebooks bases de datos interbibliotecario formacion",
        "answer": "La página de Servicios de la Biblioteca CESA enumera consulta de ebooks y búsqueda de información, préstamos de colección general, colección de reserva y dispositivos móviles, préstamo interbibliotecario, solicitud de documentos no disponibles y formación para usar recursos de información. Para préstamo interbibliotecario, solicitudes de documentos o asesorías, publica el correo serviciosbiblioteca@cesa.edu.co. La página no describe aquí un procedimiento de reserva de salas de estudio.",
        "url": LIBRARY_SERVICES_URL, "source": "CESA, Servicios de Biblioteca", "status": "verified_public", "topic": "Biblioteca",
    },
    {
        "id": "pizza", "question": "¿Dónde está la máquina de pizzas Fiamma?",
        "aliases": "pizza fiamma maquina casa diagonal 34 emprendimiento talento cesa",
        "answer": "El aviso que compartió Luis sitúa la máquina de Pizzas Fiamma en Casa Diagonal 34 I y la describe como emprendimiento de talento CESA. No pude confirmar en una fuente pública si sigue allí ni sus horarios o disponibilidad; compruébalo antes de ir.",
        "url": "", "source": "Aviso compartido por Luis, sin fecha ni fuente institucional verificable", "status": "user_supplied", "topic": "Avisos",
    },
    {
        "id": "mobility", "question": "¿Dónde respondo la encuesta de movilidad sostenible?",
        "aliases": "encuesta movilidad sostenible transporte impacto ambiental formulario",
        "answer": "Luis compartió un enlace para una encuesta de movilidad sostenible de la comunidad CESA. No pude comprobar desde aquí si el formulario sigue abierto ni quién administra las respuestas. Revisa esos datos antes de enviar información personal.",
        "url": "https://forms.cloud.microsoft/r/iewRjNrKKp", "source": "Aviso compartido por Luis, sin fecha de cierre", "status": "user_supplied", "topic": "Avisos",
    },
]

PUBLIC_PAGES = [
    STUDENTS_URL,
    REGISTRY_URL,
    CENTERS_URL,
    LIBRARY_SERVICES_URL,
    SABER_URL,
    "https://www.cesa.edu.co/calendario-academico/calendario-academico-pregrado/",
    "https://www.cesa.edu.co/experiencia-cesa/bienestar/consejeria/",
    "https://www.cesa.edu.co/financiacion-becas/",
    "https://www.cesa.edu.co/experiencia-cesa/bienestar/extracurriculares/",
    "https://www.cesa.edu.co/experiencia-cesa/campus/rutas/",
    "https://www.cesa.edu.co/experiencia-cesa/bienestar/asesoria/",
    "https://www.cesa.edu.co/experiencia-cesa/bienestar/psicologia/",
    "https://www.cesa.edu.co/sobre-el-cesa/informacion-institucional/codigos-estatutos-y-reglamentos/",
]
