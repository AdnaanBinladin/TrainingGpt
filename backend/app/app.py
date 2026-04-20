from flask import Flask, jsonify
from flask_cors import CORS

from app.routes.chat_routes import chat_blueprint
from app.routes.upload_routes import upload_blueprint


def create_app() -> Flask:
    """
    Create the Flask application.

    Keeping this as an app factory makes it easier to add per-tenant middleware,
    test configuration, auth, and observability later.
    """
    flask_app = Flask(__name__)
    CORS(flask_app)

    flask_app.register_blueprint(chat_blueprint)
    flask_app.register_blueprint(upload_blueprint)

    @flask_app.get("/health")
    def health_check():
        """Lightweight health endpoint for containers and load balancers."""
        return jsonify({"status": "ok"})

    return flask_app


app = create_app()


@app.get("/")
def root_check():
    """Root endpoint for a quick manual API check."""
    return jsonify({"service": "multi-team-rag-chatbot", "status": "ok"})
