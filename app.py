from flask import Flask, request, jsonify, render_template_string
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# Auth path for Google service account (set by Render Secret File)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/etc/secrets/gcp-key.json"

app = Flask(__name__)
credentials = service_account.Credentials.from_service_account_file("/etc/secrets/gcp-key.json")
client = bigquery.Client(credentials=credentials, project=credentials.project_id)

# Simple HTML form template
form_template = """
<!DOCTYPE html>
<html>
<head>
    <title>Heart Disease Predictor</title>
    <style>
        body { font-family: Arial; background: #f2f2f2; padding: 20px; max-width: 600px; margin: auto; }
        input { padding: 10px; width: 100%; margin: 10px 0; }
        button { padding: 10px; background-color: #007bff; color: white; border: none; width: 100%; }
    </style>
</head>
<body>
    <h2>Heart Disease Prediction</h2>
    <form method="post" action="/">
        {% for field in fields %}
            <label>{{ field }}</label>
            <input type="number" name="{{ field }}" required>
        {% endfor %}
        <button type="submit">Predict</button>
    </form>
    {% if prediction is not none %}
        <h3>Prediction: {{ prediction }}</h3>
    {% endif %}
</body>
</html>
"""

fields = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs',
          'restecg', 'thalch', 'exang', 'oldpeak', 'slope', 'ca', 'thal']

@app.route("/", methods=["GET", "POST"])
def home():
    prediction = None
    if request.method == "POST":
        try:
            data = {field: request.form[field] for field in fields}
            query = f"""
            SELECT predicted_target
            FROM ML.PREDICT(MODEL heartdisease-463313.diseasedataset.disease_model,
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
                )
            )
            """
            results = client.query(query).result()
            for row in results:
                prediction = int(row["predicted_target"])
        except Exception as e:
            prediction = f"Error: {str(e)}"
    return render_template_string(form_template, fields=fields, prediction=prediction)

@app.route("/predict", methods=["POST"])
def predict_api():
    try:
        data = request.get_json()
        query = f"""
        SELECT predicted_target
        FROM ML.PREDICT(MODEL heartdisease-463313.diseasedataset.disease_model,
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
            )
        )
        """
        results = client.query(query).result()
        for row in results:
            return jsonify({"prediction": int(row["predicted_target"])})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host="0.0.0.0", port=port)