from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

from flask import Flask, render_template, request
from sort_drive import sort_drive_files

# other code in app.py

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

if __name__ == '__main__':
    app.run(debug=True)
