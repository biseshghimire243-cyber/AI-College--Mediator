
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "success": True,
        "project": "AI College Assistant",
        "message": "Welcome to the AI College Assistant API!",
        "version": "1.0.0"
    })


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "success": True,
        "status": "healthy",
        "message": "Python backend is working"
    })


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


if __name__ == "__main__":
    app.run(debug=True, port=5000)
