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

    for archivo in archivos:
        with open(os.getenv('FILES_PATH') + archivo, "r", encoding="utf-8") as entrada, \
                open(os.getenv('CLEAN_FILES') + archivo, "w", encoding="utf-8") as salida:

            linea_anterior = entrada.readline()

            for linea_actual in entrada:
                linea_actual = linea_actual.strip()

                if linea_actual.startswith("RT "):
                    continue

                if not re.match(r"^\d{19}", linea_actual):
                    linea_actual = re.sub(r"https?://\S+", "", linea_actual)
                    linea_actual = re.sub(r"@[A-Za-z0-9_]+", "", linea_actual)
                    linea_actual = re.sub(r"#\w+", "", linea_actual)

                    palabras = linea_actual.split()
                    palabras_filtradas = [palabra for palabra in palabras if palabra.lower() not in stopwords]
                    linea_actual = ' '.join(palabras_filtradas)

                    linea_anterior += " " + linea_actual
                else:
                    salida.write(linea_anterior + "\n")
                    linea_anterior = linea_actual

            if linea_anterior.strip():
                salida.write(linea_anterior + "\n")


def load_info():

    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())

    try:
        tweets = []
        archivos = [archivo for archivo in os.listdir(os.getenv('FILES_PATH')) if archivo.endswith(".txt")]
        database = client.get_database('elecciones')

        clean_file(archivos)
        for archivo in archivos:
            with open(os.getenv('CLEAN_FILES') + archivo, "r", encoding="utf-8") as archivo2:
                lineas = archivo2.readlines()

            nombre_coleccion = archivo[:-4]
            print(nombre_coleccion)
            coleccion = database.create_collection(nombre_coleccion)
            print(coleccion)

            tweet_actual = {}  # Diccionario para almacenar un tweet
            for linea in lineas:
                if linea.strip():
                    match = re.match(r"^\d{19}", linea)
                    if match:
                        if tweet_actual:
                            tweets.append(tweet_actual)
                            coleccion.insert_one(tweet_actual)
                        tweet_actual = {"ID": match.group(), "texto": ""}
                        tweet_actual["texto"] += linea[20:]
                    else:
                        tweet_actual["texto"] += linea

    except Exception as e:
        print(e)