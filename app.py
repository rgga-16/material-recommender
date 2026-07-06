"""Entry point: python app.py"""
from server import create_app
from server.config import PORT, STATIC_IMDIR
from server.services import scene_store

app = create_app()

if __name__ == "__main__":
    scene_store.init(STATIC_IMDIR)
    app.run(debug=False, port=PORT, threaded=True)
