from flask import Flask
from flask_cors import CORS
from config import FRONTEND_URL
from routes.subjects import bp as subjects_bp
from routes.grades import bp as grades_bp
from routes.assignments import bp as assignments_bp
from routes.exams import bp as exams_bp
from routes.attendances import bp as attendances_bp



# Creates and configures the Flask app. Registers the blueprints for all of the features the SMP provides.
def create_app():
    app = Flask(__name__)

    # Lock CORS down to the frontend origin only
    CORS(app, origins=[FRONTEND_URL])
    app.register_blueprint(subjects_bp, url_prefix='/api/subjects')
    app.register_blueprint(grades_bp, url_prefix='/api/grades')
    app.register_blueprint(assignments_bp, url_prefix='/api/assignments')
    app.register_blueprint(exams_bp, url_prefix='/api/exams')
    app.register_blueprint(attendances_bp, url_prefix='/api/attendance')
    return app

# Run app on debug mode to test the code.
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
