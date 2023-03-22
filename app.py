from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
from sqlalchemy import create_engine
import requests
import json
from requests.structures import CaseInsensitiveDict
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import word_tokenize
import string
from gensim import corpora
from gensim.models.ldamodel import LdaModel
import re
from urllib.parse import urlparse
import tldextract


app = Flask(__name__)

# Your existing code for the homepage, Google Calendar, and OneNote integration
# OneNote API functions
def preprocess_domain(domain):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()

    domain_parts = domain.lower().split(".")
    stop_free = " ".join([i for i in domain_parts if i not in stop])
    punc_free = "".join(ch for ch in stop_free if ch not in exclude)
    normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())

    return normalized

def sort_websites(text, num_categories=3):
    urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', text)
    domains = [tldextract.extract(url).domain for url in urls]

    preprocessed_domains = [preprocess_domain(domain) for domain in domains]

    # Tokenize the preprocessed domains
    tokens = [word_tokenize(domain) for domain in preprocessed_domains]

    # Create a dictionary and corpus for LDA
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(token) for token in tokens]

    # Train the LDA model
    lda_model = LdaModel(corpus, num_topics=num_categories, id2word=dictionary, passes=50)

    # Sort the domains into categories
    sorted_data = {f"Category {i}": [] for i in range(1, num_categories + 1)}

    for doc in corpus:
        topic_distribution = lda_model.get_document_topics(doc)
        most_likely_topic = max(topic_distribution, key=lambda x: x[1])[0]
        sorted_data[f"Category {most_likely_topic + 1}"].append(urls[corpus.index(doc)])

    formatted_data = ""
    for category, items in sorted_data.items():
        formatted_data += f"<h3>{category}</h3><ul>"
        for item in items:
            formatted_data += f"<li><a href='{item}' target='_blank'>{item}</a></li>"
        formatted_data += "</ul>"

    return formatted_data


def create_page(access_token, section_id, content):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {access_token}"

    data = {
        "title": "Sorted notes",
        "content": f"<html><head><title>Sorted notes</title></head><body>{content}</body></html>",
    }

    response = requests.post(
        f"https://graph.microsoft.com/v1.0/me/onenote/sections/{section_id}/pages",
        headers=headers,
        data=json.dumps(data),
    )

    if response.status_code == 201:
        print("Page created successfully")
    else:
        print("Error creating page:", response.text)

def get_sections(access_token):
    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/json"
    headers["Authorization"] = f"Bearer {access_token}"

    response = requests.get(
        "https://graph.microsoft.com/v1.0/me/onenote/sections",
        headers=headers,
    )

    if response.status_code == 200:
        sections = response.json()["value"]
        return sections
    else:
        print("Error fetching sections:", response.text)
        return None

# Text preprocessing function
def preprocess(text):
    stop = set(stopwords.words('english'))
    exclude = set(string.punctuation)
    lemma = WordNetLemmatizer()

    def clean(doc):
        stop_free = " ".join([i for i in doc.lower().split() if i not in stop])
        punc_free = "".join(ch for ch in stop_free if ch not in exclude)
        normalized = " ".join(lemma.lemmatize(word) for word in punc_free.split())
        return normalized

    return clean(text)

# Text sorting function using LDA
def sort_text(text, num_topics=3):
    preprocessed_text = preprocess(text)

    # Tokenize the preprocessed text
    tokens = [word_tokenize(doc) for doc in preprocessed_text]

    # Create a dictionary and corpus for LDA
    dictionary = corpora.Dictionary(tokens)
    corpus = [dictionary.doc2bow(token) for token in tokens]

    # Train the LDA model
    lda_model = LdaModel(corpus, num_topics=num_topics, id2word=dictionary, passes=50)

    # Sort the text into topics
    sorted_data = {f"Topic {i}": [] for i in range(1, num_topics + 1)}
    for i, topic in enumerate(lda_model.show_topics(formatted=False, num_words=5)):
        sorted_data[f"Topic {i + 1}"] = [word[0] for word in topic[1]]

    # Create a formatted string to represent the sorted data as bullet points
    formatted_data = ""
    for topic, items in sorted_data.items():
        formatted_data += f"<h3>{topic}</h3><ul>"
        for item in items:
            formatted_data += f"<li>{item}</li>"
        formatted_data += "</ul>"

    return formatted_data

def process_and_create_onenote_page(access_token, section_id, text):
    sorted_data = sort_text(text, num_topics=3)
    create_page(access_token, section_id, sorted_data)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['GET', 'POST'])
def process_text():
    result = None
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        section_id = request.form.get('section_id')
        text = request.form.get('text')

        if access_token and section_id and text:
            process_and_create_onenote_page(access_token, section_id, text)
            result = "Successfully sorted text and created a new page in OneNote."

    return render_template('process_text.html', result=result)



@app.route('/subpage', methods=['GET', 'POST'])
def subpage():
    result = None
    if request.method == 'POST':
        # Call your Python script here and store the result in the 'result' variable
        try:
            credentials_file = 'credentials.json'
            folder_id = 'your_folder_id_here'
            sort_drive_files(credentials_file, folder_id)
            result = "Successfully sorted files in Google Drive folder."
        except Exception as e:
            result = f"An error occurred: {str(e)}"

    return render_template('subpage.html', result=result)

@app.route('/upload', methods=['POST'])
def upload():
    csvfile = request.files.get('csvfile')
    database_name = request.form.get('database_name')
    table_name = request.form.get('table_name')

    if csvfile and database_name and table_name:
        data = pd.read_csv(csvfile)
        engine = create_engine(f'sqlite:///{database_name}')
        data.to_sql(table_name, engine, if_exists='replace', index=False)
        return render_template('csv_to_sql.html')

    return redirect(url_for('index'))

@app.route('/view_data', methods=['GET'])
def view_data():
    database_name = request.args.get('database_name')
    table_name = request.args.get('table_name')

    if database_name and table_name:
        engine = create_engine(f'sqlite:///{database_name}')
        data = pd.read_sql_table(table_name, engine)
        return render_template('view_data.html', data=data.to_html(), table_name=table_name, database_name=database_name)

    return redirect(url_for('index'))

@app.route('/sort_urls', methods=['GET', 'POST'])
def sort_urls():
    result = None
    if request.method == 'POST':
        text = request.form.get('text')

        if text:
            result = sort_websites(text)

    return render_template('sort_urls.html', result=result)

# Add the following line to your main() function

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3666, debug=True)

