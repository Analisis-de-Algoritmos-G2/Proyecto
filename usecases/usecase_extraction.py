import os
import re
import certifi
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi


def write_twitter_content(file, tweets):

    file_name = file + '.txt'
    with open(os.getenv('FILES_PATH') + file_name, 'w', encoding='utf-8') as f:
        for tweet in tweets:
            f.write(f"{tweet.id}\t{tweet.rawContent}\n")


def get_stopwords(file):
    text = ""
    with open(file, "r") as archivo:
        text = archivo.read()

    palabras = text.split(",")

    return set(palabras)


def clean_file(archivos):

    stopwords = get_stopwords(os.getenv("UTILS_FILES"))
    emoji_pattern = re.compile("["
                               u"\U0001F600-\U0001F64F"  # Emoticonos de caritas
                               u"\U0001F300-\U0001F5FF"  # Símbolos y pictogramas
                               u"\U0001F680-\U0001F6FF"  # Transporte y mapas
                               u"\U0001F700-\U0001F77F"  # Símbolos de alquimia
                               u"\U0001F780-\U0001F7FF"  # Símbolos
                               u"\U0001F800-\U0001F8FF"  # Símbolos de signos de jerga
                               u"\U0001F900-\U0001F9FF"  # Símbolos suplementarios y pictogramas
                               u"\U0001FA00-\U0001FA6F"  # Símbolos de ajedrez
                               u"\U0001FA70-\U0001FAFF"  # Símbolos de ajedrez
                               u"\U0001F004-\U0001F0CF"  # Símbolos de juego de cartas
                               u"\U0001F170-\U0001F251"  # Símbolos de letras en círculos
                               u"\U0001F300-\U0001F5FF"  # Símbolos y pictogramas
                               u"\u2714"
                               u"\u2066\u2069"
                               u"\u007C"                       
                               "]+", flags=re.UNICODE)

    for archivo in archivos:
        with open(os.getenv('FILES_PATH') + archivo, "r", encoding="utf-8") as entrada, \
                open(os.getenv('CLEAN_FILES') + archivo, "w", encoding="utf-8") as salida:

            linea_anterior = entrada.readline()

            for linea_actual in entrada:
                linea_actual = linea_actual.strip()

                if linea_actual[20:].startswith("RT "):
                    continue

                if not re.match(r"^\d{19}", linea_actual):
                    linea_actual = re.sub(r"https?://\S+", "", linea_actual)
                    linea_actual = re.sub(r"@[A-Za-z0-9_]+", "", linea_actual)
                    linea_actual = re.sub(r"#\w+", "", linea_actual)
                    linea_actual = emoji_pattern.sub(r'', linea_actual)

                    palabras = linea_actual.split()
                    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in stopwords]
                    linea_actual = ' '.join(palabras_filtradas).replace(' a ', '')
                    linea_actual = linea_actual.replace('a ', '')
                    linea_actual = linea_actual.replace(',', '')

                    linea_anterior += " " + linea_actual
                else:
                    linea_actual = re.sub(r"https?://\S+", "", linea_actual)
                    linea_actual = re.sub(r"@[A-Za-z0-9_]+", "", linea_actual)
                    linea_actual = re.sub(r"#\w+", "", linea_actual)
                    linea_actual = emoji_pattern.sub(r'', linea_actual)
                    palabras = linea_actual.split()
                    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in stopwords]
                    linea_actual = ' '.join(palabras_filtradas).replace(' a ', '')
                    linea_actual = linea_actual.replace('a ', '')
                    linea_actual = linea_actual.replace(',', '')

                    salida.write(linea_anterior.lower() + "\n")
                    linea_anterior = linea_actual

            if linea_anterior.strip():
                salida.write(linea_anterior.lower() + "\n")


def load_info():

    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    try:
        tweets = []
        archivos = [archivo for archivo in os.listdir(os.getenv('FILES_PATH')) if archivo.endswith(".txt")]
        database = client.get_database('elecciones')

        for archivo in archivos:
            count = 0
            with open(os.getenv('CLEAN_FILES') + archivo, "r", encoding="utf-8") as archivo2:
                lineas = archivo2.readlines()

            nombre_coleccion = archivo[:-4]
            coleccion = database.create_collection(nombre_coleccion)
            print(coleccion)

            tweet_actual = {}  # Diccionario para almacenar un tweet
            for linea in lineas:
                if linea.strip():

                    match = re.match(r"^\d{19}", linea)
                    if match:
                        if tweet_actual:
                            tweets.append(tweet_actual)
                            count += 1
                            if count < 120:
                                coleccion.insert_one(tweet_actual)
                        tweet_actual = {"ID": match.group(), "texto": ""}
                        tweet_actual["texto"] += linea[20:]
                    else:
                        tweet_actual["texto"] += linea

    except Exception as e:
        print(e)