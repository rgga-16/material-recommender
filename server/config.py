import os

# Repo root (parent of the server/ package)
CWD = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

STATIC_IMDIR = os.path.join(CWD, "client", "public")
SERVER_IMDIR = os.path.join(STATIC_IMDIR, "gen_images")
SERVER_PRESET_IMDIR = os.path.join(STATIC_IMDIR, "preset_materials")
# Path prefix the browser uses to reach generated images (relative to client/public)
CLIENT_IMDIR = "gen_images"

DATA_DIR = os.path.join(CWD, "data")
MODELS_3D_DIR = os.path.join(DATA_DIR, "3d_models")
SCENES_DIR = os.path.join(DATA_DIR, "scenes")

# Bundled demo scene used to bootstrap the current scene on first launch
DEMO_SCENE = "pool-side-small"

PORT = 2099
