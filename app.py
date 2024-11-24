import os
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import json
from datetime import datetime

INDEX_NAME = os.getenv('INDEX_NAME', 'webhook-data')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5000))
ES_HOST = os.getenv('ES_HOST', 'http://localhost:9200')
ES_USER = os.getenv('ES_USER')
ES_PASSWORD = os.getenv('ES_PASSWORD')

app = Flask(__name__)

if ES_USER and ES_PASSWORD:
    es = Elasticsearch(
        [ES_HOST],
        http_auth=(ES_USER, ES_PASSWORD)
    )
else:
    es = Elasticsearch([ES_HOST])

@app.route('/alert', methods=['POST'])
def webhook():
    data = request.json

    if not data:
        return jsonify({"error": "Invalid JSON data"}), 400

    timestamp = datetime.utcnow().isoformat() + "Z" 

    document = {
        "timestamp": timestamp,
        "data": data
    }

    try:
        res = es.index(index=INDEX_NAME, body=document)
        return jsonify({"status": "success"}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to index data: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=FLASK_PORT)
