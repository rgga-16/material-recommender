"""Entry point: python app.py"""
import logging

from server import create_app
from server.config import HOST, PORT, SERVER_THREADS, STATIC_IMDIR
from server.services import scene_store

log = logging.getLogger(__name__)

app = create_app()

if __name__ == "__main__":
    scene_store.init(STATIC_IMDIR)
    try:
        from waitress import serve
    except ImportError:
        log.warning("waitress not installed (pip install -r requirements.txt); "
                    "falling back to the Flask dev server")
        app.run(debug=False, host=HOST, port=PORT, threaded=True)
    else:
        log.info("serving on http://%s:%s", HOST, PORT)
        serve(app, host=HOST, port=PORT, threads=SERVER_THREADS)
