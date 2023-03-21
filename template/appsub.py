from flask import Flask, render_template, request
from sort_drive import sort_drive_files

app = Flask(__name__)

# Your existing code for the homepage, Google Calendar, and OneNote integration

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

@app.route('/csv_to_sql', methods=['GET', 'POST'])
def csv_to_sql():
    # Your existing code for uploading CSV and converting it to SQL

# Add the following line to your main() function
app.run(host='0.0.0.0', port=3666)

if __name__ == '__main__':
    main()
