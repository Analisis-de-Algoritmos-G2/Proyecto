import os
import asyncio
from twscrape import API, gather
from usecases import usecase_extraction, usecase_process
from dotenv import load_dotenv
import ssl

# Desactivar la verificación del certificado SSL
ssl._create_default_https_context = ssl._create_unverified_context


async def main():

    # Get credentials from environment variables
    username = os.getenv('TWITTER_USERNAME')
    password = os.getenv('TWITTER_PASSWORD')
    email = os.getenv('TWITTER_EMAIL')
    email_password = os.getenv('TWITTER_EMAIL_PASSWORD')

    candidates = ['JERobledo', 'GustavoBolivar', 'CarlosFGalan', 'Rodrigo_Lara_', 'Diego_Molano', 'JDOviedoA']

    # Delete existing database
    if os.path.exists("accounts.db"):
        os.remove("accounts.db")

    api = API()  # or API("path-to.db") - default is `accounts.db`

    # ADD ACCOUNTS
    await api.pool.add_account(username, password, email, email_password)
    await api.pool.login_all()

    for candidate in candidates:
        user = await api.user_by_login(candidate)

        tweets = await gather(api.user_tweets(user.id, limit=100))  # Adjust limit as needed

        usecase_extraction.write_twitter_content(candidate, tweets)

    # Use a search query to get tweets based on specific keywords
    query = "candidato AND encuesta AND alcaldía AND Bogotá"

    tweets = await gather(api.search(query, limit=100))  # Adjust limit as needed

    usecase_extraction.write_twitter_content('general', tweets)


if __name__ == "__main__":

    load_dotenv()

    asyncio.run(main())

    e_files = [archivo for archivo in os.listdir(os.getenv('FILES_PATH')) if archivo.endswith(".txt")]

    usecase_extraction.clean_file(e_files)
    c_files = [archivo for archivo in os.listdir(os.getenv('CLEAN_FILES')) if archivo.endswith(".txt")]

    usecase_extraction.load_info()

    usecase_process.get_feeling_textblob(c_files)
    feelings = usecase_process.get_feeling_nltk(c_files)
    print(feelings)

    usecase_process.create_cloud_words(c_files)

    topics = usecase_process.get_principal_topics(c_files)
    print(topics)

    pares = usecase_process.get_pair(topics)
    print(pares)




