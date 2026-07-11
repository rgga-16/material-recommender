"""server.paths: URL <-> disk translation and the traversal guard."""
import os

import pytest

from server.config import STATIC_IMDIR
from server.paths import PathNotAllowedError, resolve_public_path, to_public_url, to_public_url_maybe


def test_url_roundtrip():
    url = "gen_images/renderings/current/rendering.png"
    resolved = resolve_public_path(url)
    assert resolved.startswith(os.path.realpath(STATIC_IMDIR))
    assert to_public_url(resolved) == url


def test_leading_slash_and_backslashes():
    assert to_public_url(resolve_public_path("/gen_images/x.png")) == "gen_images/x.png"
    assert to_public_url(resolve_public_path("gen_images\\sub\\x.png")) == "gen_images/sub/x.png"


def test_absolute_path_inside_public():
    abs_path = os.path.join(STATIC_IMDIR, "gen_images", "y.png")
    assert to_public_url(abs_path) == "gen_images/y.png"


@pytest.mark.parametrize("bad", [
    "../app.py",
    "gen_images/../../requirements.txt",
    "..\\..\\secrets.txt",
    "",
    None,
    123,
])
def test_traversal_rejected(bad):
    with pytest.raises(PathNotAllowedError):
        resolve_public_path(bad)


def test_absolute_path_outside_public_rejected():
    outside = os.path.join(os.path.dirname(os.path.realpath(STATIC_IMDIR)), "app.py")
    with pytest.raises(PathNotAllowedError):
        resolve_public_path(outside)


def test_maybe_passthrough():
    assert to_public_url_maybe(None) is None
    assert to_public_url_maybe("") == ""
    assert to_public_url_maybe("../outside.png") == "../outside.png"
    assert to_public_url_maybe("gen_images/z.png") == "gen_images/z.png"
