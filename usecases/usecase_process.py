import re

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

        for linea in lineas:
            partes = linea.strip().split('\t')
            if len(partes) == 2:
                tweet_id = re.match(r"^\d{19}", linea).group()
                tweet = partes[1]
                sentiment = analyzer.polarity_scores(tweet)

                # Clasificar el sentimiento en positivo, negativo o neutro
                if sentiment['compound'] > 0.05:
                    positivos += 1
                elif sentiment['compound'] < -0.05:
                    negativos += 1
                else:
                    neutrales += 1

                actualizar_registro_mongodb(tweet_id, sentiment)

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
    # Establecer la conexión a la base de datos MongoDB
    uri = os.getenv('MONGODB_CLIENT')

    client = MongoClient(uri, server_api=ServerApi('1'), tlsCAFile=certifi.where())
    database = client.get_database('elecciones')
    collection = database.get_collection(nombre)

    # Actualizar el registro en MongoDB
    collection.update_one(
        {"ID": tweet_id},
        {"$set": {"sentimiento_positivo": sentiment['pos'], "sentimiento_negativo": sentiment['neg']}}
    )

    # Cerrar la conexión a la base de datos
    client.close()


