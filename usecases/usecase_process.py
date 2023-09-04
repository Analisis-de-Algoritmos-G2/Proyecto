import re
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import certifi
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from textblob import TextBlob
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os


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

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
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


def create_cloud_words(files):

    stopwords = get_stopwords(os.getenv('UTILS_FILES'))

    for file in files:
        with open(os.getenv('CLEAN_FILES') + file, 'r', encoding='utf-8') as file2:
            texto = file2.read()

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


def get_pair(topics):
    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')
    topics.pop(0)
    final = []

    for topic in topics:
        pairs = []
        collection = database.get_collection(topic[-1])
        for word in topic:
            tweet_n = "No hay par"
            tweet_p = "No hay par"
            word = word.replace(".", "").lower()
            sentimientos_p = collection.find({
                "Sentimiento": "Positivo"
            })
            sentimientos_n = collection.find({
                "Sentimiento": "Negativo"
            })

            for sentimiento in sentimientos_n:
                if word in sentimiento["texto"].lower():
                    tweet_n = sentimiento["texto"]

            for sentimiento in sentimientos_p:
                if word in sentimiento["texto"].lower():
                    tweet_n = sentimiento["texto"]

            tweets = {
                "Palabra": word,
                "Positivo": tweet_p,
                "Negativo": tweet_n,
            }

            pairs.append(tweets)

        result = {
            "Nombre": topic[-1],
            "Pares": pairs,
        }
        final.append(result)

    return final
