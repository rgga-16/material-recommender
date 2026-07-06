"""Flask application factory."""
import sys

# Vendored code (DeepBump) prints non-ASCII; keep Windows consoles happy.
for stream in (sys.stdout, sys.stderr):
    if stream is not None and hasattr(stream, "reconfigure"):
        stream.reconfigure(errors="replace")

from flask import Flask

from server.config import STATIC_IMDIR


def create_app():
    app = Flask(__name__, static_folder=STATIC_IMDIR)

    from server.routes import assistant, scenes, static, textures
    app.register_blueprint(scenes.bp)
    app.register_blueprint(textures.bp)
    app.register_blueprint(assistant.bp)
    app.register_blueprint(static.bp)  # last: has the catch-all /<path>

    return app
