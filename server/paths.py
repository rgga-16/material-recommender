"""Translation and validation between disk paths and client-facing URLs.

The canonical client-facing form of any file under client/public is a
public-relative URL path with forward slashes and no leading slash, e.g.
``gen_images/renderings/current/rendering.png``. The browser can GET it
directly, and every route that accepts a path from the client resolves it
back to disk through resolve_public_path(), which refuses anything that
escapes client/public.
"""
import os

from server.config import STATIC_IMDIR

_PUBLIC_ROOT = os.path.realpath(STATIC_IMDIR)


class PathNotAllowedError(ValueError):
    """A client-supplied path points outside client/public."""


def _is_real_abs(path):
    """True for genuinely absolute paths (drive/UNC on Windows), not for
    URL-style '/gen_images/...' strings."""
    if os.name == "nt":
        return bool(os.path.splitdrive(path)[0])
    return os.path.isabs(path)


def resolve_public_path(path):
    """Resolve a client-supplied path/URL to an absolute path inside
    client/public. Raises PathNotAllowedError otherwise."""
    if not isinstance(path, str) or not path.strip():
        raise PathNotAllowedError("empty path")
    path = path.strip()
    if _is_real_abs(path):
        candidate = path
    else:
        candidate = os.path.join(_PUBLIC_ROOT, path.lstrip("/\\"))
    resolved = os.path.realpath(candidate)
    try:
        inside = os.path.commonpath(
            [os.path.normcase(_PUBLIC_ROOT), os.path.normcase(resolved)]
        ) == os.path.normcase(_PUBLIC_ROOT)
    except ValueError:  # different drives
        inside = False
    if not inside:
        raise PathNotAllowedError(f"path outside client/public: {path!r}")
    return resolved


def to_public_url(path):
    """Convert a disk path under client/public to its public URL form
    (forward slashes, no leading slash). Raises PathNotAllowedError if the
    path is not under client/public."""
    resolved = resolve_public_path(path)
    rel = os.path.relpath(resolved, _PUBLIC_ROOT)
    return rel.replace(os.sep, "/")


def to_public_url_maybe(path):
    """to_public_url(), but passes through values that aren't public paths
    (None, already-external URLs, files outside client/public)."""
    if not isinstance(path, str) or not path.strip():
        return path
    try:
        return to_public_url(path)
    except PathNotAllowedError:
        return path
