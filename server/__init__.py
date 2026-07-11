"""Flask application factory."""
import logging
import sys

# Vendored code (DeepBump) prints non-ASCII; keep Windows consoles happy.
for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException

from server.config import STATIC_IMDIR
from server.http import ValidationError
from server.paths import PathNotAllowedError

log = logging.getLogger(__name__)


def configure_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def create_app():
    configure_logging()
    app = Flask(__name__, static_folder=STATIC_IMDIR)

    from server.routes import assistant, autostyle, presets, scenes, static, textures
    app.register_blueprint(scenes.bp)
    app.register_blueprint(textures.bp)
    app.register_blueprint(presets.bp)
    app.register_blueprint(autostyle.bp)
    app.register_blueprint(assistant.bp)
    app.register_blueprint(static.bp)  # last: has the catch-all /<path>

    @app.errorhandler(ValidationError)
    def _bad_request(e):
        return jsonify({"error": e.message}), 400

    @app.errorhandler(PathNotAllowedError)
    def _forbidden(e):
        log.warning("rejected client path: %s", e)
        return jsonify({"error": "path outside the public directory"}), 403

    @app.errorhandler(FileNotFoundError)
    def _not_found(e):
        return jsonify({"error": str(e)}), 404

    @app.errorhandler(Exception)
    def _internal(e):
        if isinstance(e, HTTPException):
            return e
        log.exception("unhandled error")
        return jsonify({"error": "internal server error"}), 500

    return app
