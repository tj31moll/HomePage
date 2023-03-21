from flask import Flask, render_template, request, redirect, url_for
from sort_drive import sort_drive_files
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


app = Flask(__name__)

# Your existing code for the homepage, Google Calendar, and OneNote integration

@app.route('/process_text', methods=['GET', 'POST'])
def process_text():
    result = None
    if request.method == 'POST':
        access_token = request.form.get('access_token')
        section_id = request.form.get('section_id')
        text = request.form.get('text')

        if access_token and section_id and text:
            sorted_data = sort_text(text, num_topics=3)
            create_page(access_token, section_id, sorted_data)
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

# Add the following line to your main() function

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3666, debug=True)

