"""Server-side design brief store.

The brief is the single source of truth for every assistant prompt (chat,
suggestions, feedback, texture prompt enrichment) — it is always injected
server-side, the client never sends it. Persisted as a small JSON file so it
survives restarts; editable via GET/POST /design_brief or a PDF upload.
"""
import json
import logging
import os
import threading

from server.config import DESIGN_BRIEF_PATH

log = logging.getLogger(__name__)

_lock = threading.Lock()

DEFAULT_BRIEF = """\
Design Brief for a Family Poolside Patio

Client Demographics: The clients are a family of four with two young children. They live in a coastal area in the Philippines and love spending time outdoors. They want to create a poolside patio that is both functional and stylish, where the whole family can relax and have fun.

Background: The family recently had a pool installed in their backyard and wants to create a poolside patio that complements the pool and provides them with a space to entertain guests and spend time as a family.

Preferred Design Style: The family prefers a coastal design style with natural textures, light colors, and a relaxed vibe. They want the design to be cohesive with their home's coastal interior design, which features a lot of white and blue hues.

Desired Feel and Ambience: The family wants the poolside patio to have a fun and relaxed feel, with a touch of sophistication. They want the space to be perfect for both daytime and nighttime use, with soft lighting that creates a cozy and inviting atmosphere.

Colors, Materials, and Finishes: The family prefers a color scheme that is light and airy, with shades of blue and green to complement the pool. They want the materials and finishes to be durable and low-maintenance, while also being natural.

Budget: The budget for the project is moderate.

Furniture:
Four patio lounge chairs
Two patio sidetables
Two outdoor umbrellas
An outdoor sofa
Two outdoor sofa chairs
A coffee table
An outdoor pool
Outdoor flooring
An outdoor dining table
Five outdoor dining chairs

Planned Uses: The poolside patio will be used for entertaining guests, lounging by the pool, and dining al fresco. The lounge chairs and umbrellas will be used for sunbathing and relaxing by the pool, while the outdoor sofa and chairs will be used for lounging and socializing. The dining table and chairs will be used for outdoor dining, and the coffee table will be used for drinks and snacks.

Location: The poolside patio will be located in a coastal area in the Philippines. The environment will be tropical, with a lot of greenery and a warm climate. The design will take inspiration from the coastal surroundings, with natural textures and colors that blend in with the environment.
"""


def get_brief() -> str:
    with _lock:
        try:
            with open(DESIGN_BRIEF_PATH, encoding="utf-8") as f:
                brief = json.load(f).get("brief", "")
        except FileNotFoundError:
            return DEFAULT_BRIEF
        except (OSError, ValueError):
            log.warning("could not read design brief file", exc_info=True)
            return DEFAULT_BRIEF
    return brief if brief.strip() else DEFAULT_BRIEF


def set_brief(text: str) -> None:
    with _lock:
        os.makedirs(os.path.dirname(DESIGN_BRIEF_PATH), exist_ok=True)
        with open(DESIGN_BRIEF_PATH, "w", encoding="utf-8") as f:
            json.dump({"brief": text}, f, ensure_ascii=False, indent=2)
