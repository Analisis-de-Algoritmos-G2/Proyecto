import re
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import certifi
from pymongo import MongoClient, TEXT
from pymongo.server_api import ServerApi
from textblob import TextBlob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
from selenium import webdriver
import time

extraction_candidatos = {
    "Galan": "utils/files/extraction/CarlosFGalan.txt",
    "Oviedo": "utils/files/extraction/JDOviedoA.txt",
    "Lara": "utils/files/extraction/Rodrigo_Lara_.txt",
    "Robledo": "utils/files/extraction/JERobledo.txt",
    "Bolivar": "utils/files/extraction/GustavoBolivar.txt",
    "Molano": "utils/files/extraction/Diego_Molano.txt",
}

clean_candidatos = {
    "Galan": "utils/files/clean/CarlosFGalan.txt",
    "Oviedo": "utils/files/clean/JDOviedoA.txt",
    "Lara": "utils/files/clean/Rodrigo_Lara_.txt",
    "Robledo": "utils/files/clean/JERobledo.txt",
    "Bolivar": "utils/files/clean/GustavoBolivar.txt",
    "Molano": "uutils/files/clean/Diego_Molano.txt",
}

def filtrar_palabras_por_tema(ruta_archivo, palabras_clave):
    # Contenedor para las líneas filtradas
    lineas_filtradas = []

    # Abrir el archivo y leer línea por línea
    with open(ruta_archivo, 'r') as archivo:
        for linea in archivo:
            # Verificar si alguna de las palabras clave está en la línea
            if any(palabra in linea.lower() for palabra in palabras_clave):
                lineas_filtradas.append(linea.strip())  # Añadir la línea sin espacios adicionales

    return ", ".join(lineas_filtradas)

def get_feeling_nltk(archivos):
    nltk.download('vader_lexicon')
    analyzer = SentimentIntensityAnalyzer()

    resultados = []

    for archivo in archivos:
        positivos = 0
        negativos = 0
        neutrales = 0
        with open(os.getenv('CLEAN_FILES') + archivo, 'r', encoding='utf-8') as archivo2:
            lineas = archivo2.readlines()

        nombre = archivo.split(".")[0]
        sentimiento = ""
        istweet = False
        for linea in lineas:
            istweet = False
            if re.match(r"^\d{19}", linea):
                tweet_id = re.match(r"^\d{19}", linea).group()
                tweet = linea[20:]
                istweet = True
            else:
                tweet = linea
            sentiment = analyzer.polarity_scores(tweet)

            if sentiment['compound'] > 0.05:
                positivos += 1
                sentimiento = "Positivo"
            elif sentiment['compound'] < -0.05:
                negativos += 1
                sentimiento = "Negativo"
            else:
                neutrales += 1
                sentimiento = "Neutral"

            if istweet:
                actualizar_registro_mongodb(tweet_id, sentimiento, nombre)

        total_tweets = len(lineas)
        porcentaje_positivos = (positivos / total_tweets) * 100
        porcentaje_negativos = (negativos / total_tweets) * 100
        porcentaje_neutrales = (neutrales / total_tweets) * 100

        # Imprimir los resultados
        nombre = archivo.split(".")[0]
        resultado = {
            "Nombre": nombre,
            "Total de tweets": total_tweets,
            "Tweets positivos": f"{positivos} ({porcentaje_positivos:.2f}%)",
            "Tweets negativos": f"{negativos} ({porcentaje_negativos:.2f}%)",
            "Tweets neutrales": f"{neutrales} ({porcentaje_neutrales:.2f}%)",
        }
        resultados.append(resultado)

    return resultados


def get_feeling_textblob(archivos):

    for archivo in archivos:
        positivos = 0
        negativos = 0
        neutrales = 0
        with open(os.getenv('CLEAN_FILES') + archivo, 'r', encoding='utf-8') as archivo2:
            lineas = archivo2.readlines()

        # Analizar el sentimiento de cada tweet
        for linea in lineas:
            # Dividir la línea en ID de tweet y contenido de tweet
            partes = linea.strip().split('\t')
            if len(partes) == 2:
                tweet = partes[1]
                analysis = TextBlob(tweet)

                # Calcular la polaridad del sentimiento (positivo, negativo o neutro)
                if analysis.sentiment.polarity > 0:
                    positivos += 1
                elif analysis.sentiment.polarity < 0:
                    negativos += 1
                else:
                    neutrales += 1

        # Calcular el porcentaje de cada sentimiento
        total_tweets = len(lineas)
        porcentaje_positivos = (positivos / total_tweets) * 100
        porcentaje_negativos = (negativos / total_tweets) * 100
        porcentaje_neutrales = (neutrales / total_tweets) * 100

        # Imprimir los resultados
        nombre = archivo.split(".")[0]
        #print(f"\n\n-----Análisis de Sentimiento de {nombre} --------")
        #print("\tTotal de tweets:", total_tweets)
        #print("\tTweets positivos:", positivos, f"({porcentaje_positivos:.2f}%)")
        #print("\tTweets negativos:", negativos, f"({porcentaje_negativos:.2f}%)")
        #print("\tTweets neutrales:", neutrales, f"({porcentaje_neutrales:.2f}%)")

def actualizar_registro_mongodb(tweet_id, sentiment, nombre):
    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, tlsCAFile=certifi.where())
    database = client.get_database('elecciones')
    collection = database.get_collection(nombre)

    # Actualizar el registro en MongoDB
    collection.update_one(
        {"ID": tweet_id},
        {"$set": {'Sentimiento': sentiment}}
    )

    # Cerrar la conexión a la base de datos
    client.close()

def get_stopwords(file):
    text = ""
    with open(file, "r") as archivo:
        text = archivo.read()

    palabras = text.split(",")
    return set(palabras)


def create_cloud_words(files, palabras_clave):

    stopwords = get_stopwords(os.getenv('UTILS_FILES'))

    for file in files:
        texto = filtrar_palabras_por_tema(os.getenv('CLEAN_FILES') + file, palabras_clave)

        wordcloud = WordCloud(stopwords=stopwords,
                              background_color='white',
                              width=800,
                              height=800,
                              max_words=200,
                              colormap='viridis').generate(texto)

        plt.figure(figsize=(10, 10))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')

        nombre = file.split(".")[0]
        output_path = os.path.join(os.getenv('DIAGRAM_FOLDER'), f'{nombre}_wordcloud.png')

        plt.savefig(output_path, bbox_inches='tight')


def get_principal_topics(files):
    matriz = [[]]
    stopwords = get_stopwords(os.getenv('UTILS_FILES'))
    for file in files:
        words = []
        with open(os.getenv('CLEAN_FILES') + file, "r") as archivo:
            text = archivo.read()
            texto = re.sub(r"^\d{19}", "", text, flags=re.IGNORECASE)

        documents = [documento.split() for documento in texto.split('\n')]

        diccionario = corpora.Dictionary(documents)
        corpus = [diccionario.doc2bow(documento) for documento in documents]

        modelo_lda = LdaModel(corpus, id2word=diccionario, num_topics=5)
        results = []

        for idx, topic in modelo_lda.print_topics(-1):
            words = re.findall(r'"(.*?)"', topic)
            result = [palabra for palabra in words if palabra.lower() not in stopwords]
            if "." in result:
                result.remove(".")
            elif "-" in result:
                result.remove("-")
            elif "a" in result:
                result.remove("a")
            elif "," in result:
                result.remove(",")

            results = [elemento for elemento in result if not (
                        isinstance(elemento, int) or (isinstance(elemento, str) and elemento.isdigit()))]
            results.append(file.split('.')[0])
        matriz.append(results)

    return matriz

def get_tweet(collection, text):
    regex_pattern = "|".join(text)
    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')

    collectioncandi = database.get_collection(collection)

    collectioncandi.create_index([("texto", TEXT)])

    sentimientos_p = collectioncandi.find({
        "$text": {"$search": regex_pattern},
        "Sentimiento": "Positivo"
    })

    for sentimiento in sentimientos_p:
        tweet_p = sentimiento["texto"]
        return tweet_p


def buscar_string(archivo, string_a_buscar):
    palabras_clave = string_a_buscar.split()

    # Abrir el archivo en modo lectura
    with open(clean_candidatos.get(archivo), 'r', encoding='utf-8') as file:  # Asegúrate de usar la codificación correcta
        for numero_linea, linea in enumerate(file, 1):
            # Verificar si todas las palabras clave están en la línea
            if all(palabra in linea for palabra in palabras_clave):
                id = linea.split()[0]
                return buscar_id(extraction_candidatos.get(archivo), id)
    return "El string no fue encontrado."

def buscar_id(archivo, string_a_buscar):
    # Convertir el string en una lista de palabras
    palabras_clave = string_a_buscar.split()

    # Abrir el archivo en modo lectura
    with open(archivo, 'r', encoding='utf-8') as file:  # Asegúrate de usar la codificación correcta
        for numero_linea, linea in enumerate(file, 1):
            # Verificar si todas las palabras clave están en la línea
            if all(palabra in linea for palabra in palabras_clave):
                return f"{linea}"
    return "El string no fue encontrado."

def get_tweetNeg(collection, text):
    regex_pattern = "|".join(text)
    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')

    collectioncandi = database.get_collection(collection)

    collectioncandi.create_index([("texto", TEXT)])

    sentimientos_n = collectioncandi.find({
        "$text": {"$search": regex_pattern},
        "Sentimiento": "Negativo"
    })

    for sentimiento in sentimientos_n:
        tweet_n = sentimiento["texto"]
        return tweet_n

def get_2(collection):
    uri = os.getenv('MONGODB_CLIENT')
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')

    collectioncandi = database.get_collection(collection)

    conteo_negativos = collectioncandi.count_documents({
        "Sentimiento": "Negativo"
    })
    conteo_positivos = collectioncandi.count_documents({
        "Sentimiento": "Positivo"
    })
    conteo_neutrales = collectioncandi.count_documents({
        "Sentimiento": "Neutral"
    })

    return {"Positivos": conteo_positivos, "Negativos": conteo_negativos, "Neutrales": conteo_neutrales}

def get_count(collection):
    uri = os.getenv('MONGODB_CLIENT')
    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')

    collectioncandi = database.get_collection(collection)

    conteo_negativos = collectioncandi.count_documents({
        "Sentimiento": "Negativo"
    })
    conteo_positivos = collectioncandi.count_documents({
        "Sentimiento": "Positivo"
    })
    conteo_neutrales = collectioncandi.count_documents({
        "Sentimiento": "Neutral"
    })

    response = "Positivos: " + str(conteo_positivos) + "\nNegativos: " + str(conteo_negativos) + "\nNeutrales: " + str(conteo_neutrales)
    return response

def get_general():
    # URL de la página que contiene el canvas
    url = 'https://elpais.com/america-colombia/2023-10-05/galan-lidera-las-encuestas-para-la-alcaldia-de-bogota-sin-una-victoria-asegurada.html'

    # Creamos una nueva instancia de un navegador
    driver = webdriver.Chrome()

    try:
        # Ir a la URL
        driver.get(url)

        # Dar tiempo al navegador para cargar y ejecutar JavaScript
        time.sleep(5)  # Puedes necesitar ajustar este tiempo

        # Encontrar el elemento canvas por su selector
        canvas = driver.find_element_by_css_selector('canvas[aria-hidden="true"]')

        # Aquí es donde se pone complicado: los datos dentro del canvas han sido dibujados usando JavaScript,
        # y no hay una manera directa de extraerlos. En su lugar, puedes pedirle a Selenium que tome una captura de pantalla.

        # Guardar el contenido del canvas como una imagen PNG
        canvas.screenshot('canvas.png')
    finally:
        # Cerrar el navegador
        driver.quit()


