from flask import Flask, render_template,request
import pyodbc
import requests

app = Flask(__name__)

# database connection config 
server = 'serverclo.database.windows.net'
database = 'dbapp'
username = 'hind'
password = 'Lul66611'

conn_str = f'Driver={{ODBC Driver 18 for SQL Server}};Server=tcp:serverclo.database.windows.net,1433;Database=dbapp;Uid=hind;Pwd=Lul66611;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'
conn = pyodbc.connect(conn_str)
cursor = conn.cursor()

# Azure Custom Vision API configuration
api_url = "https://customvisionqualcontrol-prediction.cognitiveservices.azure.com/customvision/v3.0/Prediction/b71a3ebb-d7bc-4811-9cdf-58211f986d76/classify/iterations/Iteration3/image"
api_key = "d531f24aeeef4a1aa9a138fbeff6539c"
headers = {
    "Prediction-Key": api_key,
    "Content-Type": "application/octet-stream"
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyser')
def analyser():
    return render_template('hind.html')

@app.route('/dashboard')
def dashboard():
    return render_template('2.html')

@app.route('/result', methods=['POST'])
def result():
    idserie_value = request.form.get('idserie', '')
    try:
        conn = pyodbc.connect(conn_str)
        cursor = conn.cursor()

        print(f"ID Serie Value: {idserie_value}")
        cursor.execute("SELECT idserie, nom, COUNT(*) as nombre_defectueux FROM articles WHERE etat = 'défectueuse' GROUP BY idserie, nom")
        # Debugging: Print the executed SQL query
        # sql_query = "SELECT idserie, nom, COUNT(*) as nombre_defectueux FROM articles WHERE etat = 'défectueuse' AND idserie = ? GROUP BY idserie, nom"
        # print(f"SQL Query: {sql_query}")
        
        # cursor.execute(sql_query, idserie_value)
        rows = cursor.fetchall()
        print(rows)

        # Render the result template or redirect to another page
        return render_template('result.html', rows=rows)

    except Exception as e:
        # Handle exceptions, you might want to log the error
        return render_template('error.html', error=str(e))

    finally:
        cursor.close()
        conn.close()





@app.route('/analyser', methods=['POST'])
def analyse():
    try:
        
        # Retrieve the image file from the form data
        file = request.files['fileUpload']
        image_file = file.read()


        # The API request
        response = requests.post(api_url, headers=headers, data=image_file)

        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            # Process the classification results
            predictions = result.get('predictions', [])
            # Do something with the predictions
            print("Classification results:", predictions)
            return render_template('predictions.html', predictions=predictions)

        else:
            print("Error:", response.status_code, response.text)
            return render_template('predictions.html', predictions=predictions)

    except Exception as e:
        print("An error occurred:", str(e))
        import traceback
        traceback.print_exc()  # Add this line to print the full traceback
        return render_template('error.html', error=str(e))
    else:
        # Add this return statement to handle the case when the API request is not successful
        return render_template('error.html', error="Unknown error occurred")
if __name__ == '__main__':
    app.run(debug=True)
