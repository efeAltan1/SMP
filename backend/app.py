from flask import Flask
from flask_cors import CORS
from config import FRONTEND_URL
from routes.subjects import bp as subjects_bp
from routes.grades import bp as grades_bp
from routes.exams import bp as exams_bp
from routes.attendances import bp as attendance_bp
from routes.announcements import bp as announcements_bp
from routes.analytics import bp as analytics_bp
from routes.sync import bp as sync_bp





# creates and configures the Flask app
def create_app():
    app = Flask(__name__)

    # lock CORS down to the frontend origin only. Registering blueprints for the features.
    CORS(app, origins=[FRONTEND_URL])
    app.register_blueprint(subjects_bp, url_prefix='/api/subjects')
    app.register_blueprint(grades_bp, url_prefix='/api/grades')
    app.register_blueprint(exams_bp, url_prefix='/api/exams')
    app.register_blueprint(attendance_bp, url_prefix='/api/attendance')
    app.register_blueprint(announcements_bp, url_prefix='/api/announcements')
    app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
     
    return app

# run app on debug mode
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
