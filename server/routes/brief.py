"""Design brief routes (view/edit/PDF import) and client app config."""
import logging

from flask import Blueprint, jsonify

from server.config import FEEDBACK_DEBOUNCE_S, FEEDBACK_MIN_INTERVAL_S
from server.http import ValidationError, get_json_body, require_fields
from server.services import design_brief

bp = Blueprint("brief", __name__)

log = logging.getLogger(__name__)

# Guard against runaway extractions (a brief is a page or two of text).
_MAX_BRIEF_CHARS = 20000


@bp.route("/design_brief", methods=["GET"])
def get_design_brief():
    return jsonify({"brief": design_brief.get_brief()})


@bp.route("/design_brief", methods=["POST"])
def set_design_brief():
    brief = require_fields(get_json_body(), "brief")
    if not isinstance(brief, str) or not brief.strip():
        raise ValidationError("brief must be a non-empty string")
    design_brief.set_brief(brief.strip()[:_MAX_BRIEF_CHARS])
    return jsonify({"brief": design_brief.get_brief()})


@bp.route("/design_brief_pdf", methods=["POST"])
def set_design_brief_pdf():
    from flask import request
    if "file" not in request.files:
        raise ValidationError("no file provided")
    file = request.files["file"]
    try:
        from pypdf import PdfReader
        reader = PdfReader(file.stream)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception:
        log.warning("PDF extraction failed", exc_info=True)
        raise ValidationError("could not read that PDF; is it a text-based PDF?")
    text = text.strip()
    if not text:
        raise ValidationError("no text found in the PDF (scanned image PDFs "
                              "are not supported)")
    design_brief.set_brief(text[:_MAX_BRIEF_CHARS])
    return jsonify({"brief": design_brief.get_brief()})


@bp.route("/app_config", methods=["GET"])
def app_config():
    """Client-facing knobs (proactive feedback pacing)."""
    return jsonify({
        "feedback_debounce_s": FEEDBACK_DEBOUNCE_S,
        "feedback_min_interval_s": FEEDBACK_MIN_INTERVAL_S,
    })
