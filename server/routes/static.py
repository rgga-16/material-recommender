"""Serves the compiled Svelte app and static assets."""
import os

from flask import Blueprint, send_from_directory

from server.config import STATIC_IMDIR

bp = Blueprint("static_pages", __name__)


@bp.route("/")
def base():
    return send_from_directory(STATIC_IMDIR, "index.html")


@bp.route("/<path:path>")
def assets(path):
    return send_from_directory(STATIC_IMDIR, path)
