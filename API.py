from flask import Flask, request, send_file, jsonify
from dotenv import load_dotenv
import os
from flask_cors import CORS, cross_origin
from usecases import usecase_process

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:4200"}})

load_dotenv()

e_files = [archivo for archivo in os.listdir(os.getenv('FILES_PATH')) if archivo.endswith(".txt")]
c_files = [archivo for archivo in os.listdir(os.getenv('CLEAN_FILES')) if archivo.endswith(".txt")]
response = ""
imagenes_candidatos = {
    "Galan": "utils/files/diagrams/CarlosFGalan_wordcloud.png",
    "Oviedo": "utils/files/diagrams/JDOviedoA_wordcloud.png",
    "Lara": "utils/files/diagrams/CarlosFGalan_wordcloud.png",
    "Robledo": "utils/files/diagrams/Rodrigo_Lara__wordcloud.png",
    "Bolivar": "utils/files/diagrams/GustavoBolivar_wordcloud.png",
    "Molano": "utils/files/diagrams/Diego_Molano_wordcloud.png",
}


twitter_candi = {
    "Galan": "CarlosFGalan",
    "Oviedo": "JDOviedoA",
    "Lara": "Rodrigo_Lara_",
    "Robledo": "JERobledo",
    "Bolivar": "GustavoBolivar",
    "Molano": "Diego_Molano",
}

palabras_clave_movilidad = [
    "transporte",
    "tráfico",
    "congestión",
    "metro",
    "bicicleta",
    "peatón",
    "automóvil",
    "carretera",
    "autobús",
    "moto",
    "semáforo",
    "carril",
    "taxi",
    "vehículo",
    "estacionamiento",
    "acera",
    "intersección",
    "rotonda",
    "puente",
    "autopista",
    "túnel",
    "movilidad",
    "transitabilidad",
    "transporte público",
    "electromovilidad",
    "sostenibilidad",
    "compartir coche",
    "scooter",
    "transporte activo",
    "vías",
    "infraestructura",
    "movilidad sostenible",
    "transporte no motorizado",
    "zona peatonal",
    "ciclovía",
    "ciclismo urbano",
    "contaminación del aire",
    "emisiones",
    "combustible",
    "movilidad eléctrica",
    "vehículo autónomo",
    "vehículo conectado",
    "teleférico",
    "monopatín",
    "pasajero",
    "tarifa",
    "ruta",
    "horario",
    "acceso",
    "conexión",
    "integración",
    "multimodal",
    "logística",
    "desplazamiento",
    "planificación urbana",
    "seguridad vial",
    "accesibilidad",
    "congestión vehicular",
    "flota",
    "normativa",
    "regulación",
    "política pública",
    "ordenamiento territorial",
    "desarrollo urbano",
    "sistema de transporte",
    "red vial",
    "movilidad activa",
    "espacio público"
]
palabras_clave_seguridad = [
    "seguridad",
    "policía",
    "patrullaje",
    "delito",
    "crimen",
    "prevención",
    "violencia",
    "emergencia",
    "protección",
    "vigilancia",
    "orden",
    "ley",
    "justicia",
    "criminalidad",
    "investigación",
    "arresto",
    "detención",
    "autoridad",
    "peligro",
    "riesgo",
    "amenaza",
    "defensa",
    "fuerzas",
    "armada",
    "conflicto",
    "rescate",
    "terrorismo",
    "extorsión",
    "secuestro",
    "hurto",
    "robo",
    "asalto",
    "vandalismo",
    "pandilla",
    "narcotráfico",
    "contrabando",
    "corrupción",
    "fraude",
    "soborno",
    "cohecho",
    "impunidad",
    "cárcel",
    "prisión",
    "reclusión",
    "pena",
    "juicio",
    "fiscalía",
    "demanda",
    "querella",
    "acusación",
    "testimonio",
    "evidencia",
    "culpabilidad",
    "inocencia",
    "sentencia",
    "apelación",
    "indemnización",
    "compensación",
    "restricción",
    "cautela",
    "alerta",
    "sospecha",
    "intervención",
    "operativo",
    "emergencia",
    "crisis",
    "tragedia",
    "víctima",
    "lesiones",
    "fatalidad",
    "socorro",
    "auxilio",
    "refugio",
    "evacuación",
    "contingencia",
    "planificación",
    "estrategia",
    "táctica",
    "protocolo",
    "normativa",
    "regulación",
    "política",
    "reforma",
    "derechos",
    "libertades",
    "civiles",
    "privacidad",
    "confidencialidad",
    "integridad",
    "ética",
    "moral",
    "conciencia",
    "responsabilidad",
    "compromiso",
    "servicio",
    "comunidad",
    "sociedad",
    "ciudadanía",
    "participación",
    "cooperación",
    "colaboración",
    "asociación",
    "alianza",
    "fuerza",
    "unidad",
    "solidaridad",
    "resiliencia",
    "superación",
    "progreso",
    "mejora",
    "avance",
    "innovación",
    "tecnología",
    "ciencia",
    "conocimiento",
    "educación",
    "formación",
    "capacitación",
    "habilidad",
    "destreza",
    "eficacia",
    "eficiencia",
    "calidad",
    "excelencia",
    "satisfacción",
    "confianza",
    "credibilidad",
    "reputación",
    "prestigio",
    "honor",
    "respeto",
    "dignidad",
    "orgullo",
    "valor",
    "coraje",
    "valentía",
    "heroísmo",
    "sacrificio",
    "lealtad",
    "fidelidad",
    "honestidad",
    "integridad",
    "veracidad",
    "autenticidad",
    "genuinidad",
    "sinceridad",
    "franqueza",
    "transparencia",
    "claridad",
    "lucidez",
    "percepción",
    "comprensión",
    "entendimiento",
    "conocimiento",
    "sabiduría",
    "inteligencia",
    "raciocinio",
    "lógica",
    "razón",
    "sentido",
    "significado",
    "propósito",
    "intención",
    "motivación",
    "inspiración",
    "pasión",
    "entusiasmo",
    "optimismo",
    "esperanza",
    "fe",
    "creencia",
    "convicción",
    "certeza",
    "seguridad",
    "garantía",
    "protección",
    "salvaguarda",
    "defensa",
    "resistencia",
    "oposición",
    "rechazo",
    "negación",
    "refutación",
    "desmentido",
    "contradicción"
]
palabras_clave_educacion = [
    "educación",
    "enseñanza",
    "aprendizaje",
    "escuela",
    "colegio",
    "universidad",
    "academia",
    "estudio",
    "estudiante",
    "maestro",
    "profesor",
    "docente",
    "pedagogía",
    "didáctica",
    "currículum",
    "programa",
    "curso",
    "asignatura",
    "lección",
    "examen",
    "evaluación",
    "calificación",
    "diploma",
    "título",
    "beca",
    "matrícula",
    "investigación",
    "tesis",
    "seminario",
    "conferencia",
    "taller",
    "práctica",
    "laboratorio",
    "biblioteca",
    "libro",
    "texto",
    "lectura",
    "escritura",
    "aritmética",
    "ciencia",
    "tecnología",
    "ingeniería",
    "matemáticas",
    "historia",
    "geografía",
    "lengua",
    "literatura",
    "filosofía",
    "arte",
    "cultura",
    "deporte",
    "disciplina",
    "respeto",
    "responsabilidad",
    "colaboración",
    "honestidad",
    "creatividad",
    "innovación",
    "pensamiento",
    "crítico",
    "solución",
    "problemas",
    "comunicación",
    "liderazgo",
    "empatía",
    "inclusión",
    "diversidad",
    "equidad",
    "acceso",
    "calidad",
    "excelencia",
    "rendimiento",
    "mejora",
    "reforma",
    "política",
    "financiación",
    "acreditación",
    "certificación",
    "alfabetización",
    "digital",
    "virtual",
    "remota",
    "e-learning",
    "m-learning",
    "plataforma",
    "interactiva",
    "recurso",
    "educativo",
    "orientación",
    "vocacional",
    "profesional",
    "carrera",
    "empleabilidad",
    "prácticas",
    "pasantías",
    "graduación",
    "alumnado",
    "tutoría",
    "mentoría",
    "asesoramiento",
    "bienestar",
    "estudiantil",
    "participación",
    "comunidad",
    "asociación",
    "padres",
    "madres",
    "familia",
    "hogar",
    "apoyo",
    "refuerzo",
    "extraescolar",
    "enriquecimiento",
    "intervención",
    "temprana",
    "especial",
    "necesidades",
    "adaptación",
    "curricular",
    "individualizado",
    "desarrollo",
    "personal",
    "social",
    "emocional",
    "psicológico",
    "salud",
    "mental",
    "física",
    "nutrición",
    "recreación",
    "ocio",
    "juego",
    "creativo",
    "expresión",
    "artística",
    "musical",
    "danza",
    "teatro",
    "pintura",
    "escultura",
    "poesía",
    "narrativa",
    "cuento",
    "novela",
    "ensayo",
    "crónica",
    "reportaje",
    "investigativo",
    "crítico",
    "analítico",
    "reflexivo",
    "argumentativo",
    "persuasivo",
    "narrativo",
    "descriptivo",
    "expositivo",
    "claro",
    "coherente",
    "conciso",
    "preciso",
    "correcto",
    "formal",
    "informal",
    "académico",
    "científico",
    "técnico",
    "profesional",
    "laboral",
    "empresarial",
    "comercial",
    "publicitario",
    "periodístico",
    "literario",
    "popular",
    "colaborativo",
    "cooperativo",
    "autónomo",
    "independiente",
    "autodidacta",
    "proactivo",
    "motivado",
    "interesado",
    "curioso",
    "explorador",
    "investigador",
    "descubridor",
    "creador",
    "inventor",
    "innovador",
    "emprendedor",
    "líder",
    "gestor",
    "organizador",
    "planificador",
    "estratega",
    "analista",
    "evaluador",
    "crítico",
    "opinador",
    "comentarista",
    "revisor",
    "editor",
    "corrector",
    "traductor",
    "intérprete",
    "mediador",
    "facilitador",
    "orientador",
    "asesor",
    "consultor",
    "especialista",
    "experto",
    "profesional",
    "técnico",
    "operativo",
    "administrativo",
    "directivo",
    "ejecutivo",
    "supervisor",
    "coordinador",
    "jefe",
    "director",
    "gerente",
    "presidente",
    "secretario",
    "tesorero",
    "vocal",
    "miembro",
    "socio",
    "colaborador",
    "aliado",
    "partner",
    "compañero",
    "camarada",
    "amigo",
    "conocido",
    "contacto",
    "referente",
    "autoridad",
    "influencer",
    "celebridad",
    "figura",
    "personalidad",
    "carácter",
    "individuo",
    "persona",
    "ser",
    "humano",
    "ciudadano",
    "miembro",
    "parte",
    "elemento",
    "componente",
    "factor",
    "aspecto",
    "característica",
    "propiedad",
    "atributo",
    "cualidad",
    "virtud",
    "talento",
    "habilidad",
    "destreza",
    "capacidad"
]

@app.route('/create-word-cloud', methods=['POST'])
def create_word_cloud():
    candidate_name = request.json.get('candidate_name')
    topic = request.json.get('topic')
    if topic == 'Seguridad':
        usecase_process.create_cloud_words(c_files, palabras_clave_seguridad)
    if topic == 'Movilidad':
        usecase_process.create_cloud_words(c_files, palabras_clave_movilidad)
    if topic == 'Educacion':
        usecase_process.create_cloud_words(c_files, palabras_clave_educacion)
    image_path = imagenes_candidatos.get(candidate_name)

    if image_path:
        try:
            # Si la ruta existe, envía el archivo
            return send_file(image_path, mimetype='image/png')
        except Exception as e:
            # Manejo básico de errores, ajustar según sea necesario
            return jsonify({'error': 'Error al enviar el archivo: {}'.format(e)}), 500
    else:
        # Si no se encuentra el candidato, devuelve un mensaje de error
        return jsonify({'error': 'Candidato no encontrado'}), 404


@app.route('/get_positive_tweet', methods=['POST'])
def get_positive_tweet():
    candidate_name = request.json.get('candidate_name')
    topic = request.json.get('topic')

    tweet = ""

    if topic == 'Seguridad':
        tweet = usecase_process.get_tweet(twitter_candi.get(candidate_name), palabras_clave_seguridad)
    if topic == 'Movilidad':
        tweet = usecase_process.get_tweet(twitter_candi.get(candidate_name), palabras_clave_movilidad)
    if topic == 'Educacion':
        tweet = usecase_process.get_tweet(twitter_candi.get(candidate_name), palabras_clave_educacion)

    if tweet:
        tweet_completo = usecase_process.buscar_string(candidate_name, tweet)
        return tweet_completo  # If a tweet is found based on the conditions, return it.
    else:
        response = f"El candidato {candidate_name} no tiene tweets positivos acerca de {topic}"
        return response

@app.route('/get_negative_tweet', methods=['POST'])
@cross_origin()
def get_negative_tweet():
    candidate_name = request.json.get('candidate_name')
    topic = request.json.get('topic')

    tweet = ""

    if topic == 'Seguridad':
        tweet = usecase_process.get_tweetNeg(twitter_candi.get(candidate_name), palabras_clave_seguridad)
    if topic == 'Movilidad':
        tweet = usecase_process.get_tweetNeg(twitter_candi.get(candidate_name), palabras_clave_movilidad)
    if topic == 'Educacion':
        tweet = usecase_process.get_tweetNeg(twitter_candi.get(candidate_name), palabras_clave_educacion)

    if tweet:
        tweet_completo = usecase_process.buscar_string(candidate_name, tweet)
        return tweet_completo
    else:
        response = f"El candidato {candidate_name} no tiene tweets negativos acerca de {topic}"
        return response

@app.route('/get_count', methods=['POST'])
@cross_origin()
def get_count():
    candidate_name=request.json.get('candidate_name')

    response = usecase_process.get_count(twitter_candi.get(candidate_name))
    return response

@app.route('/get_winner', methods=['POST'])
@cross_origin()
def get_winner():
    candidate_name1 = request.json.get('candidate_name1')
    candidate_name2 = request.json.get('candidate_name2')

    count_1 = usecase_process.get_2(twitter_candi.get(candidate_name1))
    count_2 = usecase_process.get_2(twitter_candi.get(candidate_name2))

    positivos_1 = (count_1.get("Positivos"))
    positivos_2 = (count_2.get("Positivos"))

    negativos_1 = (count_1.get("Negativos"))
    negativos_2 = (count_2.get("Negativos"))

    neutrales_1 = (count_1.get("Neutrales"))
    neutrales_2 = (count_2.get("Neutrales"))

    if positivos_1 > positivos_2:
        return candidate_name1
    elif positivos_1 == positivos_2:
        if negativos_1 > negativos_2:
            return candidate_name2
        else:
            return candidate_name1
    else:
        return candidate_name2


if __name__ == '__main__':
    app.run(debug=True)