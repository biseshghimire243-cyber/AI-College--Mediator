
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv
import mysql.connector
import os
import re

# Load environment variables from backend/.env
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))

app = Flask(__name__)
CORS(app)

FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)

STOP_WORDS = {
    "the", "is", "a", "an", "i", "you", "we", "do", "does",
    "how", "what", "where", "when", "can", "could", "would",
    "please", "for", "to", "of", "in", "on", "my", "me",
    "and", "are", "find", "tell", "about", "your", "it",
    "this", "that", "with", "be", "am", "was", "were",
    "have", "has", "had", "want", "know", "information",
    "college", "campus", "ai", "assistant", "is", "there"
}


def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER", "root"),
        password=os.getenv("DB_PASSWORD", ""),
        database=os.getenv("DB_NAME", "ai_college_assistant"),
        connection_timeout=5
    )


def get_keywords(text):
    words = re.findall(r"[a-z0-9]+", text.lower())

    return {
        word for word in words
        if len(word) > 2 and word not in STOP_WORDS
    }


def get_faq_answer(message):
    question_words = get_keywords(message)

    if not question_words:
        return None

    connection = get_db_connection()

    try:
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT question, answer, category
            FROM faqs
            ORDER BY id DESC
        """)

        faqs = cursor.fetchall()
        cursor.close()

    finally:
        connection.close()

    best_faq = None
    best_score = 0

    for faq in faqs:
        faq_question = faq.get("question") or ""
        faq_category = faq.get("category") or ""
        faq_answer = faq.get("answer") or ""

        # Match question terms and category first.
        faq_question_words = get_keywords(faq_question)
        faq_category_words = get_keywords(faq_category)

        question_matches = question_words & faq_question_words
        category_matches = question_words & faq_category_words

        # Avoid letting common words in a long answer dominate.
        score = (
            len(question_matches) * 3
            + len(category_matches) * 2
        )

        # Use the answer text only as a small secondary signal.
        answer_words = get_keywords(faq_answer)
        score += len(question_words & answer_words) * 0.25

        if score > best_score:
            best_score = score
            best_faq = faq

    # Require at least one meaningful match with the FAQ question
    # or category, rather than matching only the answer.
    if best_faq and best_score >= 2:
        matched_words = (
            question_words & get_keywords(best_faq.get("question") or "")
        ) | (
            question_words & get_keywords(best_faq.get("category") or "")
        )

        if matched_words:
            return {
                "answer": best_faq["answer"],
                "category": best_faq.get("category"),
                "source": "college_faq_database"
            }

    return None


@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


@app.route("/api/health", methods=["GET"])
def health():
    try:
        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT 1")
        cursor.fetchone()
        cursor.close()
        connection.close()

        return jsonify({
            "success": True,
            "status": "healthy",
            "database": "connected"
        })

    except (mysql.connector.Error, ValueError):
        app.logger.exception("Health check failed")

        return jsonify({
            "success": False,
            "status": "unhealthy",
            "database": "disconnected"
        }), 503


@app.route("/api/college", methods=["GET"])
def college_info():
    connection = None
    cursor = None

    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, address, phone, email, website
            FROM colleges
            ORDER BY id
        """)

        colleges = cursor.fetchall()

        return jsonify({
            "success": True,
            "colleges": colleges
        })

    except mysql.connector.Error:
        app.logger.exception("Could not retrieve college information")

        return jsonify({
            "success": False,
            "message": "Unable to retrieve college information."
        }), 503

    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


@app.route("/api/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "success": False,
            "answer": "Please send your question in a valid JSON request."
        }), 400

    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({
            "success": False,
            "answer": "Your question must be text."
        }), 400

    message = message.strip()

    if not message:
        return jsonify({
            "success": False,
            "answer": "Please enter a question."
        }), 400

    if len(message) > 1000:
        return jsonify({
            "success": False,
            "answer": "Please keep your question under 1,000 characters."
        }), 400

    normalized = message.lower().strip()
    normalized = re.sub(r"[^\w\s]", "", normalized)

    greetings = {
        "hi", "hello", "hey", "good morning",
        "good afternoon", "good evening"
    }

    if normalized in greetings:
        return jsonify({
            "success": True,
            "answer": (
                "Hello! Welcome to CampusAI. "
                "I can help you with college admissions, courses, "
                "fees, examinations, and scholarships. What would "
                "you like to know?"
            ),
            "source": "greeting"
        })

    try:
        result = get_faq_answer(message)

        if result:
            return jsonify({
                "success": True,
                "answer": result["answer"],
                "category": result["category"],
                "source": result["source"]
            })

        return jsonify({
            "success": True,
            "answer": (
                "I couldn't find a reliable answer to that question "
                "in the college FAQ database. Try asking about "
                "admissions, courses, fees, examinations, or "
                "scholarships."
            ),
            "source": "fallback"
        })

    except mysql.connector.Error:
        app.logger.exception("Database error during chat")

        return jsonify({
            "success": False,
            "answer": (
                "I'm unable to access the college database right now. "
                "Please check that MySQL is running and try again."
            )
        }), 503


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=True
    )
