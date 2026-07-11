"""Small HTTP helpers shared by the route blueprints."""
from flask import jsonify, request


class ValidationError(Exception):
    """Raised for malformed request bodies; handled globally as a 400."""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def get_json_body():
    """The request's JSON body as a dict, or a 400 via ValidationError."""
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        raise ValidationError("request body must be a JSON object")
    return body


def require_fields(body, *fields):
    """Return the named fields from body, raising ValidationError (-> 400)
    listing everything that's missing. Single field -> value, several ->
    tuple of values."""
    missing = [f for f in fields if f not in body]
    if missing:
        raise ValidationError(f"missing required field(s): {', '.join(missing)}")
    values = tuple(body[f] for f in fields)
    return values[0] if len(values) == 1 else values


def error_response(message, status):
    return jsonify({"error": message}), status
