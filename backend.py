from flask import Flask, request, jsonify
import mysql.connector
import pandas as pd
import google.generativeai as genai
from pandasai import PandasAI
from pandasai.llm.google_gemini import GoogleGemini

app = Flask(__name__)

# Set up Gemini API key
GENAI_API_KEY = "AIzaSyCrHpOsW5NwczzIOhbOii03lLwWE3ToE-4"
genai.configure(api_key=GENAI_API_KEY)

# Use Google Gemini as LLM for PandasAI
llm = GoogleGemini(api_key=GENAI_API_KEY)

# Database configuration
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "dbmoney",
}

def fetch_data():
    """Fetches all transactions from the database and returns a Pandas DataFrame."""
    conn = mysql.connector.connect(**db_config)
    query = "SELECT * FROM assets UNION ALL SELECT * FROM bills"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

@app.route("/process_query", methods=["POST"])
def process_query():
    user_query = request.json.get("message", "").strip()

    if not user_query:
        return jsonify({"reply": "Please enter a valid query."})

    df = fetch_data()
    pandas_ai = PandasAI(llm)

    try:
        response = pandas_ai.run(df, prompt=user_query)
    except Exception as e:
        response = f"Error processing your request: {str(e)}"

    return jsonify({"reply": response})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
