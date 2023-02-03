from flask import Flask, send_from_directory
import random, requests, json

import os 


products = [
    "nightstand_family",
]

data_dir = os.path.join(os.getcwd(),"data","3d_models",products[0])
rendering_setup_path = os.path.join(data_dir,"rendering_setup.json")


app = Flask(__name__, static_folder="./client/public")

@app.route("/get_objects_and_parts")
def load_object_data():
    objects_data = json.load(open(rendering_setup_path))
    object_inputs = objects_data["objects"]
    return object_inputs

# Path for our main Svelte page
@app.route("/")
def base():
    return send_from_directory('./client/public', 'index.html')

# Path for all the static files (compiled JS/CSS, etc.)
@app.route("/<path:path>")
def home(path):
    return send_from_directory('./client/public', path)

if __name__ == "__main__":
    
    
    

    app.run(debug=True)
