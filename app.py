from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import sqlite3
from sqlalchemy import create_engine

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    csvfile = request.files.get('csvfile')
    database_name = request.form.get('database_name')
    table_name = request.form.get('table_name')

    if csvfile and database_name and table_name:
        data = pd.read_csv(csvfile)
        engine = create_engine(f'sqlite:///{database_name}')
        data.to_sql(table_name, engine, if_exists='replace', index=False)

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

if __name__ == '__main__':
    app.run(debug=True)
