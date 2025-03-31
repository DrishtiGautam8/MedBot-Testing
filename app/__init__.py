from flask import Flask
from app.main import main as main_app

def create_app():
    app = Flask(__name__)  # ✅ Correctly creating Flask instance
    app.register_blueprint(main_app)  # ✅ Registering Blueprint properly
    return app
