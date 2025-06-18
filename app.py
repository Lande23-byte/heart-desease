import os
from flask import Flask, render_template, request, jsonify
from google.cloud import bigquery

app = Flask(__name__)

# Securely connect to BigQuery using your JSON key
CREDENTIALS_PATH = "heartdisease-463313-a0e55a46c3e0.json"
client = bigquery.Client.from_service_account_json(CREDENTIALS_PATH)

# Home route with input form
@app.route('/', methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
        # Get form data
        age = request.form['age']
        sex = request.form['sex']
        cp = request.form['cp']
        trestbps = request.form['trestbps']
        chol = request.form['chol']
        fbs = request.form['fbs']
        restecg = request.form['restecg']
        thalch = request.form['thalch']
        exang = request.form['exang']
        oldpeak = request.form['oldpeak']
        slope = request.form['slope']
        ca = request.form['ca']
        thal = request.form['thal']

        # BigQuery prediction query
        query = f"""
        SELECT *
        FROM ML.PREDICT(MODEL `heartdisease-463313.diseasedataset.disease_model`,
        (SELECT
            {age} AS age,
            {sex} AS sex,
            {cp} AS cp,
            {trestbps} AS trestbps,
            {chol} AS chol,
            {fbs} AS fbs,
            {restecg} AS restecg,
            {thalch} AS thalch,
            {exang} AS exang,
            {oldpeak} AS oldpeak,
            {slope} AS slope,
            {ca} AS ca,
            {thal} AS thal
        ));
        """

        job = client.query(query)
        results = [dict(row) for row in job]
        prediction = results[0] if results else "No prediction available"

    return render_template('index.html', prediction=prediction)

# API route for programmatic prediction
@app.route('/predict', methods=['POST'])
def predict_api():
    data = request.json

    query = f"""
    SELECT *
    FROM ML.PREDICT(MODEL `heartdisease-463313.diseasedataset.disease_model`,
    (SELECT
        {data['age']} AS age,
        {data['sex']} AS sex,
        {data['cp']} AS cp,
        {data['trestbps']} AS trestbps,
        {data['chol']} AS chol,
        {data['fbs']} AS fbs,
        {data['restecg']} AS restecg,
        {data['thalch']} AS thalch,
        {data['exang']} AS exang,
        {data['oldpeak']} AS oldpeak,
        {data['slope']} AS slope,
        {data['ca']} AS ca,
        {data['thal']} AS thal
    ));
    """

    job = client.query(query)
    results = [dict(row) for row in job]
    return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True)
