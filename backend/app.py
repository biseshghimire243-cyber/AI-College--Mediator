
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# Home route
@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "project": "AI College Assistant",
        "message": "Welcome to the AI College Assistant API!",
        "version": "1.0.0"
    })


# Health check
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "Python backend is working"
    })


# College information
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


# Basic chat response
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
            "How can I help you with your college-related questions?"
        )

    elif any(word in question for word in ["admission", "enroll", "enrollment"]):
        answer = (
            "For admission information, please contact your college's "
            "administration office. Ask them about eligibility, required "
            "documents, application deadlines, and entrance examinations."
        )

    elif any(word in question for word in ["fee", "fees", "payment", "tuition"]):
        answer = (
            "College fees depend on the course and institution. "
            "Please check with your college administration for the latest "
            "fee structure, payment deadlines, and available scholarships."
        )

    elif any(word in question for word in ["exam", "examination", "routine", "schedule"]):
        answer = (
            "For examination routines, check your college notice board "
            "or official website. You can also contact your department "
            "for examination dates and instructions."
        )

    elif any(word in question for word in ["course", "subject", "program", "syllabus"]):
        answer = (
            "I can help with course-related questions. Please specify your "
            "program, semester, or subject so I can guide you more accurately."
        )

    elif any(word in question for word in ["scholarship", "financial aid"]):
        answer = (
            "Scholarship eligibility and application procedures vary by "
            "college. Contact the administration office to learn about "
            "merit-based scholarships, financial assistance, and deadlines."
        )

    elif any(word in question for word in ["contact", "office", "location", "address"]):
        answer = (
            "Please provide your college name so you can get more specific "
            "contact and location information."
        )

    else:
        answer = (
            "I'm your AI College Assistant. I can help with admission, fees, "
            "courses, examinations, scholarships, and student support. "
            "Please ask a specific college-related question."
        )

    return jsonify({
        "success": True,
        "answer": answer
    })


if __name__ == "__main__":
    app.run(debug=True, port=5000)
