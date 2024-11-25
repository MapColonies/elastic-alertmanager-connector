import os
from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch
import json
from datetime import datetime

PORT = 8080
INDEX_NAME = os.getenv('INDEX_NAME', 'webhook-data')
ES_HOST = os.getenv('ES_HOST', 'http://localhost:9200')
ES_USER = os.getenv('ES_USERNAME')
ES_PASSWORD = os.getenv('ES_PASSWORD')
verify_certs = os.getenv("ES_VERIFY_CERTS", "false").lower() == "true"
certificate_path = os.getenv("ES_CERT_PATH", "/opt/bitnami/elasticsearch/config/certs/ca.cert")

app = Flask(__name__)

if ES_USER and ES_PASSWORD:
    if verify_certs:
        es = Elasticsearch([ES_HOST], http_auth=(ES_USER, ES_PASSWORD), ca_certs=certificate_path, verify_certs=True)
    else:
        es = Elasticsearch([ES_HOST], http_auth=(ES_USER, ES_PASSWORD), verify_certs=False)
else:
    if verify_certs:
        es = Elasticsearch([ES_HOST], ca_certs=certificate_path, verify_certs=True)
    else:
        es = Elasticsearch([ES_HOST], verify_certs=False)        

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
    app.run(debug=True, host='0.0.0.0', port=PORT)