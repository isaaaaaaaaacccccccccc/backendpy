from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import csv
import os
from datetime import datetime

app = Flask(__name__)
CORS(app)

CSV_FILE = "/data/respostas.csv"
HEADERS = [
    "timestamp",
    "1_disciplina", "1_professor", "1_periodo",
    "2_disciplina", "2_professor", "2_periodo",
    "3_disciplina", "3_professor", "3_periodo",
    "4_disciplina", "4_professor", "4_periodo",
    "5_disciplina", "5_professor", "5_periodo",
    "6_disciplina", "6_professor", "6_periodo",
    "7_disciplina", "7_professor", "7_periodo",
    "8_disciplina", "8_professor", "8_periodo",
    "9_disciplina", "9_professor", "9_periodo",
    "10_disciplina","10_professor","10_periodo",
]

def ensure_csv():
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)

@app.route("/submit", methods=["POST"])
def submit():
    data = request.get_json()
    ranking = data.get("ranking", [])

    if len(ranking) != 10:
        return jsonify({"error": "Ranking deve ter exatamente 10 itens"}), 400

    ensure_csv()

    row = [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
    for item in ranking:
        row.append(item.get("nome", ""))
        row.append(item.get("prof", ""))
        row.append(str(item.get("periodo", "")) + "P")

    with open(CSV_FILE, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(row)

    return jsonify({"status": "ok", "message": "Resposta salva com sucesso"})

@app.route("/download", methods=["GET"])
def download():
    ensure_csv()
    return send_file(
        CSV_FILE,
        mimetype="text/csv",
        as_attachment=True,
        download_name="respostas_ranking.csv"
    )

@app.route("/stats", methods=["GET"])
def stats():
    ensure_csv()
    from collections import Counter
    scores = Counter()
    total = 0

    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            total += 1
            for pos in range(1, 11):
                disc = row.get(f"{pos}_disciplina", "")
                prof = row.get(f"{pos}_professor", "")
                if disc:
                    peso = 11 - pos
                    scores[f"{disc} ({prof})"] += peso

    ranking = [{"disciplina": k, "pontuacao": v} for k, v in scores.most_common(10)]
    return jsonify({"total_respostas": total, "ranking": ranking})

@app.route("/", methods=["GET"])
def index():
    return jsonify({"status": "API de ranking rodando", "endpoints": ["/submit POST", "/download GET", "/stats GET"]})

if __name__ == "__main__":
    ensure_csv()
    app.run(debug=True, port=5000)
