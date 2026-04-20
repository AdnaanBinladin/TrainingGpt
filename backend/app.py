import os

from app.app import app


if __name__ == "__main__":
    # Local development entrypoint.
    # Allows running the backend with: python app.py
    app.run(host="0.0.0.0", port=int(os.getenv("BACKEND_PORT", "8101")), debug=True)
