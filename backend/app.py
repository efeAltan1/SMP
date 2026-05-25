from flask import Flask
from flask_cors import CORS
from config import FRONTEND_URL
from routes.subjects import bp as subjects_bp


# creates and configures the Flask app
def create_app():
    app = Flask(__name__)

    # lock CORS down to the frontend origin only
    CORS(app, origins=[FRONTEND_URL])
    app.register_blueprint(subjects_bp, url_prefix='/api/subjects')
    return app

# run app on debug mode
if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
