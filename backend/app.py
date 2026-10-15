
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Frontend directory
FRONTEND_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend")
)


# Open the frontend homepage
@app.route("/")
def home():
    return send_from_directory(FRONTEND_DIR, "index.html")


# Serve frontend CSS, JavaScript, and other static files
@app.route("/<path:filename>")
def frontend_files(filename):
    return send_from_directory(FRONTEND_DIR, filename)


# Health check API
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "Python backend is working"
    })


# College information API
@app.route("/api/college", methods=["GET"])
def college_info():
    return jsonify({
        "success": True,
        "college": {
            "name": "AI College Assistant Demo College",
            "location": "Nepal",
            "services": [
                "Course information",
                "Admission information",
                "Fee information",
                "Exam information",
                "Student support"
            ]
        }
    })


# Chat API
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

    if any(word in question for word in ["hello", "hi", "hey"]):
        answer = (
            "Hello! Welcome to AI College Assistant. "
            "How can I help you today?"
        )
    elif any(word in question for word in ["admission", "enroll", "enrollment"]):
        answer = (
            "For admission information, contact your college administration "
            "to learn about eligibility, documents, and application deadlines."
        )
    elif any(word in question for word in ["fee", "fees", "payment", "tuition"]):
        answer = (
            "Please contact your college administration for the current "
            "fee structure and payment deadlines."
        )
    elif any(word in question for word in ["exam", "examination", "routine"]):
        answer = (
            "Check your college's official website or notice board for "
            "examination routines and announcements."
        )
    elif any(word in question for word in ["course", "subject", "program", "syllabus"]):
        answer = (
            "Please tell me your course, semester, or subject so I can "
            "provide more relevant guidance."
        )
    elif "scholarship" in question:
        answer = (
            "Contact your college administration to learn about scholarship "
            "eligibility, available programs, and application deadlines."
        )
    else:
        answer = (
            "I can help with admissions, fees, courses, examinations, "
            "scholarships, and student support. Please ask a specific question."
        )

    return jsonify({
        "success": True,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
