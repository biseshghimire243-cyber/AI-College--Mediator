
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ai_college_assistant"),
        connection_timeout=5
    )


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/api/health")
def health():
    database_status = "connected"

    try:
        connection = get_db_connection()
        connection.close()
    except mysql.connector.Error:
        database_status = "disconnected"

    return jsonify({
        "success": True,
        "status": "healthy",
        "database": database_status
    })


@app.route("/api/college")
def college_info():
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, address, phone, email, website
            FROM colleges
            ORDER BY id
        """)

        colleges = cursor.fetchall()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "colleges": colleges
        })

    except mysql.connector.Error:
        app.logger.exception("Could not retrieve college information")
        return jsonify({
            "success": False,
            "message": "Unable to retrieve college information."
        }), 500


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    question = message.lower()

    greetings = ["hello", "hi", "hey"]
    if question in greetings or question in ["good morning", "good afternoon"]:
        return jsonify({
            "success": True,
            "answer": "Hello! Welcome to CampusAI. How can I help you today?"
        })

    keywords = [
        word.strip(".,?!:;()[]{}\"'")
        for word in question.split()
    ]

    stop_words = {
        "the", "is", "a", "an", "i", "you", "we", "do", "does",
        "how", "what", "where", "when", "can", "could", "please",
        "for", "to", "of", "in", "on", "my", "me", "and", "are",
        "find", "tell", "about", "college", "your"
    }

    keywords = [
        word for word in keywords
        if len(word) > 2 and word not in stop_words
    ]

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT question, answer, category
            FROM faqs
            ORDER BY id DESC
        """)

        faqs = cursor.fetchall()
        cursor.close()
        connection.close()

        best_faq = None
        best_score = 0

        for faq in faqs:
            faq_text = (
                faq["question"] + " " +
                faq["category"] + " " +
                faq["answer"]
            ).lower()

            score = sum(
                1 for word in keywords if word in faq_text
            )

            if score > best_score:
                best_score = score
                best_faq = faq

        if best_faq and best_score > 0:
            answer = best_faq["answer"]
        else:
            answer = (
                "I couldn't find a matching answer in the college FAQ "
                "database. Please try asking about admissions, fees, "
                "examinations, or scholarships."
            )

        return jsonify({
            "success": True,
            "answer": answer,
            "source": "college_faq_database" if best_faq and best_score > 0
                      else "fallback"
        })

    except mysql.connector.Error:
        app.logger.exception("Database error during chat")

        return jsonify({
            "success": False,
            "answer": (
                "I'm unable to access the college database right now. "
                "Please check that MySQL is running and the database "
                "configuration is correct."
            )
        }), 503


if __name__ == "__main__":
    app.run(debug=True, port=5000)
