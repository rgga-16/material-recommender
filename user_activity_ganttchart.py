import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.image as mpimg
import numpy as np
from matplotlib.offsetbox import OffsetImage, AnnotationBbox

icons_dict = {
    # 'Click Object': './papers/icons/click.svg',
    'Click Object': mpimg.imread("./papers/icons/click.png"),
}

# click_icon = mpimg.imread("./papers/icons/click.png")

def get_svg_icon(svg_path, zoom=0.1):
    return OffsetImage(plt.imread(svg_path, format='svg'), zoom=zoom)

def add_icon(ax, img, x, y, zoom=0.05):
    """Adds an image at the specified coordinates (x, y) on the plot."""
    imagebox = OffsetImage(img, zoom=zoom)
    ab = AnnotationBbox(imagebox, (x, y), frameon=False)
    ax.add_artist(ab)

def get_icon_image(icon, zoom=0.1):
    """Convert icon into an image that can be displayed in the legend."""
    return OffsetImage(icon, zoom=zoom)

mg_durations = {}
cb_durations = {}

def convert_to_seconds(start_float):
    string_val = str(start_float)
    int_part_str, decimal_part_str = string_val.split(".")
    minutes = int(int_part_str)
    seconds = int(decimal_part_str)

    return minutes*60 + seconds

# List of dictionaries representing each user action
data = [
    {'User': 'P1(P)', 'Start': 0.13, 'End': 0.13, 'Task': 'Click Object'},
    {'User': 'P1(P)', 'Start': 0.20, 'End': 0.55, 'Task': 'MG - Generate'}, #wood deck
    # {'User': 'P1(P)', 'Start': 0.26, 'End': 0.32, 'Task': 'Read Brief'},
    {'User': 'P1(P)', 'Start': 0.57, 'End': 0.57, 'Task': 'MG - Apply'}, #wood deck 2
    {'User': 'P1(P)', 'Start': 0.57, 'End': 0.57, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 1.10, 'End': 1.10, 'Task': 'MG - Apply'}, #wood deck 1
    {'User': 'P1(P)', 'Start': 1.11, 'End': 1.11, 'Task': 'MG - Apply'}, #wood deck 2
    # {'User': 'P1(P)', 'Start': 1.19, 'End': 1.30, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1(P)', 'Start': 1.40, 'End': 1.40, 'Task': 'MG - Apply'}, #wood deck 1
    # {'User': 'P1(P)', 'Start': 1.43, 'End': 1.45, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1(P)', 'Start': 2.08, 'End': 2.42, 'Task': 'MG - Generate'}, #gray nonskid tiles
    {'User': 'P1(P)', 'Start': 2.52, 'End': 2.52, 'Task': 'MG - Apply'}, #gray nonskid tiles 2
    # {'User': 'P1(P)', 'Start': 2.55, 'End': 2.57, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1(P)', 'Start': 3.04, 'End': 4.11, 'Task': 'Render'}, 
    {'User': 'P1(P)', 'Start': 4.21, 'End': 4.21, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 4.27, 'End': 4.27, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1(P)', 'Start': 4.34, 'End': 5.07, 'Task': 'MG - Generate'}, #pool tiles 
    {'User': 'P1(P)', 'Start': 5.13, 'End': 5.13, 'Task': 'MG - Apply'}, #pool tiles 2
    {'User': 'P1(P)', 'Start': 5.17, 'End': 5.17, 'Task': 'MG - Apply'}, #pool tiles 4
    {'User': 'P1(P)', 'Start': 5.43, 'End': 5.54, 'Task': 'Color Texture'}, #pool tiles
    {'User': 'P1(P)', 'Start': 5.55, 'End': 5.55, 'Task': 'Click Object'}, #lounge chair seat
    {'User': 'P1(P)', 'Start': 6.20, 'End': 7.21, 'Task': 'CB - Query Material'}, #Can you suggest cloth material for the pool beds?
    {'User': 'P1(P)', 'Start': 6.45, 'End': 6.45, 'Task': 'Click Object'}, #left fence
    {'User': 'P1(P)', 'Start': 7.10, 'End': 8.21, 'Task': 'MG - Generate'}, #wood slats
    {'User': 'P1(P)', 'Start': 7.29, 'End': 7.29, 'Task': 'Click Object'}, #umbrella canopy
    {'User': 'P1(P)', 'Start': 7.30, 'End': 7.30, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 1
    {'User': 'P1(P)', 'Start': 7.44, 'End': 7.48, 'Task': 'Color Texture'}, #umbrella canopy 1
    {'User': 'P1(P)', 'Start': 8.08, 'End': 8.08, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 2
    {'User': 'P1(P)', 'Start': 8.14, 'End': 8.19, 'Task': 'Color Texture'}, #umbrella canopy 2
    {'User': 'P1(P)', 'Start': 8.23, 'End': 8.23, 'Task': 'Click Object'}, #left fence
    {'User': 'P1(P)', 'Start': 8.25, 'End': 8.25, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1(P)', 'Start': 8.33, 'End': 8.33, 'Task': 'Click Object'}, #right fence
    {'User': 'P1(P)', 'Start': 8.36, 'End': 8.36, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1(P)', 'Start': 8.41, 'End': 8.41, 'Task': 'Click Object'}, #right fence
    # {'User': 'P1(P)', 'Start': 8.49, 'End': 9.00, 'Task': 'Scale Texture'}, #right fence
    {'User': 'P1(P)', 'Start': 9.11, 'End': 10.34, 'Task': 'Render'}, 
    {'User': 'P1(P)', 'Start': 10.57, 'End': 10.57, 'Task': 'Click Object'}, #umbrella canopy 2
    {'User': 'P1(P)', 'Start': 10.59, 'End': 10.59, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1(P)', 'Start': 11.54, 'End': 12.28, 'Task': 'MG - Generate'}, #gray cloth
    {'User': 'P1(P)', 'Start': 12.41, 'End': 13.15, 'Task': 'MG - Generate'}, #cloth
    {'User': 'P1(P)', 'Start': 13.30, 'End': 13.37, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P1(P)', 'Start': 13.39, 'End': 13.39, 'Task': 'MG - Apply'}, #cloth
    {'User': 'P1(P)', 'Start': 15.30, 'End': 15.41, 'Task': 'Click Object'}, #lounge chair cushions
    # {'User': 'P1(P)', 'Start': 15.45, 'End': 15.47, 'Task': 'Scale Texture'}, #lounge chair cushions
    {'User': 'P1(P)', 'Start': 16.08, 'End': 16.45, 'Task': 'MG - Generate'}, #powdercoated
    {'User': 'P1(P)', 'Start': 17.02, 'End': 17.42, 'Task': 'Click Object'}, #umbrella poles and lounge chair frames
    {'User': 'P1(P)', 'Start': 17.43, 'End': 17.46, 'Task': 'Color Texture'}, #umbrella poles and lounge chair frames
    # {'User': 'P1(P)', 'Start': 17.48, 'End': 17.49, 'Task': 'Set Metalness'}, # 1
    # {'User': 'P1(P)', 'Start': 17.50, 'End': 17.51, 'Task': 'Set Roughness'}, # 0
    {'User': 'P1(P)', 'Start': 18.19, 'End': 18.53, 'Task': 'MG - Generate'}, #weaved
    {'User': 'P1(P)', 'Start': 19.03, 'End': 20.36, 'Task': 'MG - Generate'}, #weaved rattan, setted number to 10
    {'User': 'P1(P)', 'Start': 19.37, 'End': 20.59, 'Task': 'Render'},  
    {'User': 'P1(P)', 'Start': 21.08, 'End': 21.08, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P1(P)', 'Start': 21.10, 'End': 21.10, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1(P)', 'Start': 21.18, 'End': 21.27, 'Task': 'Click Object'}, #sofa chair frames, coffee table base
    {'User': 'P1(P)', 'Start': 21.30, 'End': 21.30, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1(P)', 'Start': 21.31, 'End': 21.31, 'Task': 'MG - Apply'}, #weaved rattan 3
    # {'User': 'P1(P)', 'Start': 21.35, 'End': 21.38, 'Task': 'Scale Texture'}, #sofa chair frames, coffee table base
    {'User': 'P1(P)', 'Start': 21.43, 'End': 21.51, 'Task': 'Color Texture'}, #sofa chair frames, coffee table base, yellow
    {'User': 'P1(P)', 'Start': 22.03, 'End': 23.39, 'Task': 'MG - Generate'}, #cotton material
    {'User': 'P1(P)', 'Start': 22.19, 'End': 22.19, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 23.30, 'End': 25.04, 'Task': 'CB - Query Material'}, #Can you suggest similar materials to gray nonskid tiles for a floor?
    {'User': 'P1(P)', 'Start': 23.42, 'End': 24.05, 'Task': 'Click Object'}, #sofa cushions and pillows
    {'User': 'P1(P)', 'Start': 24.09, 'End': 24.09, 'Task': 'MG - Apply'}, #cotton material 4
    {'User': 'P1(P)', 'Start': 24.20, 'End': 24.26, 'Task': 'Click Object'}, #sofa cushions and pillows 
    {'User': 'P1(P)', 'Start': 24.28, 'End': 24.28, 'Task': 'MG - Apply'}, #cotton material 7
    # {'User': 'P1(P)', 'Start': 24.40, 'End': 24.43, 'Task': 'Scale Texture'}, #sofa cushions and pillows 
    {'User': 'P1(P)', 'Start': 24.48, 'End': 24.48, 'Task': 'Click Object'}, #coffee table
    {'User': 'P1(P)', 'Start': 24.58, 'End': 25.51, 'Task': 'MG - Generate'}, #glass
    {'User': 'P1(P)', 'Start': 25.04, 'End': 25.04, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 25.10, 'End': 25.10, 'Task': 'CB - Apply'}, #rubber flooring
    # {'User': 'P1(P)', 'Start': 25.11, 'End': 25.13, 'Task': 'Scale Texture'}, #floor
    {'User': 'P1(P)', 'Start': 26.02, 'End': 26.02, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P1(P)', 'Start': 26.10, 'End': 26.10, 'Task': 'MG - Apply'}, #glass 3
    {'User': 'P1(P)', 'Start': 26.58, 'End': 28.10, 'Task': 'Render'}, #glass 4
    {'User': 'P1(P)', 'Start': 28.25, 'End': 29.30, 'Task': 'MG - Generate'}, #Rubber Flooring, from CB
    {'User': 'P1(P)', 'Start': 28.30, 'End': 28.30, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 28.46, 'End': 28.46, 'Task': 'Click Object'}, #right fence
    {'User': 'P1(P)', 'Start': 28.51, 'End': 28.51, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1(P)', 'Start': 29.27, 'End': 29.27, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 29.28, 'End': 29.28, 'Task': 'MG - Apply'}, #rubber floor 2
    {'User': 'P1(P)', 'Start': 29.29, 'End': 29.29, 'Task': 'MG - Apply'}, #rubber floor 4
    {'User': 'P1(P)', 'Start': 29.30, 'End': 29.30, 'Task': 'MG - Apply'}, #rubber floor 6
    {'User': 'P1(P)', 'Start': 29.31, 'End': 29.31, 'Task': 'MG - Apply'}, #rubber floor 5
    {'User': 'P1(P)', 'Start': 29.32, 'End': 29.32, 'Task': 'MG - Apply'}, #rubber floor 3
    {'User': 'P1(P)', 'Start': 29.54, 'End': 29.44, 'Task': 'MG - Generate'}, #Stone flooring
    {'User': 'P1(P)', 'Start': 30.32, 'End': 30.50, 'Task': 'Save'},
    {'User': 'P1(P)', 'Start': 30.52, 'End': 30.52, 'Task': 'Click Object'}, #floor
    {'User': 'P1(P)', 'Start': 30.55, 'End': 30.55, 'Task': 'MG - Apply'}, #stone flooring 6
    # {'User': 'P1(P)', 'Start': 31.00, 'End': 31.02, 'Task': 'Scale Texture'}, #stone flooring 4
    {'User': 'P1(P)', 'Start': 31.03, 'End': 32.26, 'Task': 'Render'}, 
    {'User': 'P1(P)', 'Start': 32.30, 'End': 32.47, 'Task': 'Save'},

    {'User': 'P2(P)', 'Start': 0.10, 'End': 0.10, 'Task': 'Click Object'}, #pool edge
    {'User': 'P2(P)', 'Start': 0.30, 'End': 1.06, 'Task': 'MG - Generate'}, #blue tiles
    {'User': 'P2(P)', 'Start': 1.20, 'End': 1.20, 'Task': 'MG - Apply'}, #blue tiles 2
    # {'User': 'P2(P)', 'Start': 1.43, 'End': 1.47, 'Task': 'Set Roughness'}, #0.1
    # {'User': 'P2(P)', 'Start': 1.53, 'End': 1.55, 'Task': 'Set Roughness'}, #0.2
    {'User': 'P2(P)', 'Start': 2.08, 'End': 2.08, 'Task': 'Click Object'}, #floor
    {'User': 'P2(P)', 'Start': 2.21, 'End': 2.55, 'Task': 'MG - Generate'}, #wood deck
    {'User': 'P2(P)', 'Start': 3.05, 'End': 3.05, 'Task': 'MG - Apply'}, #wood deck 3
    {'User': 'P2(P)', 'Start': 3.10, 'End': 3.10, 'Task': 'Click Object'}, #floor
    # {'User': 'P2(P)', 'Start': 3.14, 'End': 3.33, 'Task': 'Scale Texture'}, #40
    {'User': 'P2(P)', 'Start': 3.48, 'End': 3.48, 'Task': 'Click Object'}, #2 lounge chair cushions
    {'User': 'P2(P)', 'Start': 3.55, 'End': 4.31, 'Task': 'MG - Generate'}, #rattan
    {'User': 'P2(P)', 'Start': 3.59, 'End': 4.01, 'Task': 'Click Object'}, #2 lounge chair cushions
    {'User': 'P2(P)', 'Start': 4.45, 'End': 4.45, 'Task': 'MG - Apply'}, #rattan 1
    # {'User': 'P2(P)', 'Start': 4.49, 'End': 4.55, 'Task': 'Scale Texture'}, #10
    {'User': 'P2(P)', 'Start': 5.03, 'End': 5.03, 'Task': 'Click Object'}, #1 lounge chair frame
    {'User': 'P2(P)', 'Start': 5.10, 'End': 5.14, 'Task': 'Color Texture'}, #white (didn't work)
    {'User': 'P2(P)', 'Start': 5.15, 'End': 5.15, 'Task': 'Click Object'}, #1 lounge chair frame
    {'User': 'P2(P)', 'Start': 5.18, 'End': 5.23, 'Task': 'Color Texture'}, #white (didn't work)
    {'User': 'P2(P)', 'Start': 5.28, 'End': 5.28, 'Task': 'Click Object'}, #2 lounge chair frames
    {'User': 'P2(P)', 'Start': 5.49, 'End': 6.25, 'Task': 'MG - Generate'}, #metal, white
    {'User': 'P2(P)', 'Start': 6.33, 'End': 6.41, 'Task': 'MG - Brainstorm'}, #shiny, reflective
    {'User': 'P2(P)', 'Start': 6.55, 'End': 7.31, 'Task': 'MG - Generate'}, #metal, white, shiny, reflective
    {'User': 'P2(P)', 'Start': 7.38, 'End': 7.38, 'Task': 'MG - Apply'}, #metal, white, shiny, reflective 4
    {'User': 'P2(P)', 'Start': 7.44, 'End': 7.46, 'Task': 'Click Object'}, #2 lounge chair frames
    {'User': 'P2(P)', 'Start': 8.02, 'End': 8.02, 'Task': 'Click Object'}, #1 umbrella canopy
    {'User': 'P2(P)', 'Start': 8.32, 'End': 8.54, 'Task': 'MG - Generate'}, #green fabric
    {'User': 'P2(P)', 'Start': 9.05, 'End': 9.05, 'Task': 'MG - Apply'}, #green fabric 1
    # {'User': 'P2(P)', 'Start': 9.15, 'End': 9.19, 'Task': 'Scale Texture'}, #5
    {'User': 'P2(P)', 'Start': 9.32, 'End': 9.32, 'Task': 'Click Object'}, #1 umbrella frame
    {'User': 'P2(P)', 'Start': 9.49, 'End': 9.53, 'Task': 'MG - Brainstorm'}, #shiny, reflective, smooth 
    {'User': 'P2(P)', 'Start': 10.05, 'End': 10.41, 'Task': 'MG - Generate'}, #metal, shiny, reflective, smooth
    {'User': 'P2(P)', 'Start': 10.50, 'End': 10.50, 'Task': 'MG - Apply'}, #metal, shiny, reflective, smooth 2
    {'User': 'P2(P)', 'Start': 11.0, 'End': 11.0, 'Task': 'Click Object'}, #1 sidetable
    {'User': 'P2(P)', 'Start': 11.14, 'End': 11.49, 'Task': 'MG - Generate'}, #wood, white
    {'User': 'P2(P)', 'Start': 12.01, 'End': 12.06, 'Task': 'MG - Brainstorm'}, #shiny, reflective, smooth 
    {'User': 'P2(P)', 'Start': 12.23, 'End': 12.23, 'Task': 'MG - Apply'}, #wood 2
    # {'User': 'P2(P)', 'Start': 12.32, 'End': 12.41, 'Task': 'Set Roughness'}, #0.1
    # {'User': 'P2(P)', 'Start': 12.49, 'End': 12.55, 'Task': 'Rotate Texture'}, #90
    {'User': 'P2(P)', 'Start': 13.19, 'End': 13.25, 'Task': 'Click Object'}, #Sofa cushions
    {'User': 'P2(P)', 'Start': 13.35, 'End': 14.11, 'Task': 'MG - Generate'}, #Light blue fabric
    {'User': 'P2(P)', 'Start': 14.18, 'End': 14.18, 'Task': 'MG - Apply'}, #Light blue fabric 1
    {'User': 'P2(P)', 'Start': 14.31, 'End': 14.35, 'Task': 'Click Object'}, #Sofa frames and coffee table base  
    {'User': 'P2(P)', 'Start': 14.41, 'End': 15.15, 'Task': 'MG - Generate'}, #white rattan
    {'User': 'P2(P)', 'Start': 15.21, 'End': 15.21, 'Task': 'MG - Apply'}, #white rattan 1
    {'User': 'P2(P)', 'Start': 15.25, 'End': 15.25, 'Task': 'MG - Apply'}, #white rattan 2
    {'User': 'P2(P)', 'Start': 15.33, 'End': 15.36, 'Task': 'Color Texture'},   
    # {'User': 'P2(P)', 'Start': 15.43, 'End': 15.47, 'Task': 'Scale Texture'}, #10
    {'User': 'P2(P)', 'Start': 15.53, 'End': 15.53, 'Task': 'Click Object'}, #Floor
    {'User': 'P2(P)', 'Start': 15.57, 'End': 16.02, 'Task': 'Click Object'}, #Sofa frames and coffee table base  
    {'User': 'P2(P)', 'Start': 16.04, 'End': 16.04, 'Task': 'Click Object'}, #Coffee table top
    {'User': 'P2(P)', 'Start': 16.13, 'End': 16.49, 'Task': 'MG - Generate'}, #clear glass
    {'User': 'P2(P)', 'Start': 16.55, 'End': 16.59, 'Task': 'MG - Brainstorm'}, #smooth, reflective
    {'User': 'P2(P)', 'Start': 17.11, 'End': 17.45, 'Task': 'MG - Generate'}, #clear glass, smooth, relective
    {'User': 'P2(P)', 'Start': 17.53, 'End': 17.53, 'Task': 'MG - Apply'}, #clear glass, smooth, relective 2
    {'User': 'P2(P)', 'Start': 17.55, 'End': 17.55, 'Task': 'Click Object'}, #Coffee table top
    {'User': 'P2(P)', 'Start': 18.01, 'End': 18.04, 'Task': 'Click Object'}, #Sofa pillows
    {'User': 'P2(P)', 'Start': 18.14, 'End': 18.51, 'Task': 'MG - Generate'}, #light grey fabric
    {'User': 'P2(P)', 'Start': 18.56, 'End': 18.56, 'Task': 'MG - Apply'},  #light grey fabric 2
    {'User': 'P2(P)', 'Start': 19.03, 'End': 19.03, 'Task': 'Click Object'}, #Fences
    {'User': 'P2(P)', 'Start': 19.18, 'End': 19.53, 'Task': 'MG - Generate'}, #oak wood
    {'User': 'P2(P)', 'Start': 20.06, 'End': 20.06, 'Task': 'MG - Apply'},  #oak wood 4
    {'User': 'P2(P)', 'Start': 20.26, 'End': 20.25, 'Task': 'Color Texture'}, 
    {'User': 'P2(P)', 'Start': 20.29, 'End': 20.31, 'Task': 'Click Object'}, #Fences
    {'User': 'P2(P)', 'Start': 20.57, 'End': 21.01, 'Task': 'Click Object'}, #Other 2 patio chair cushions
    {'User': 'P2(P)', 'Start': 21.16, 'End': 21.50, 'Task': 'MG - Generate'}, #rattan
    {'User': 'P2(P)', 'Start': 22.07, 'End': 22.07, 'Task': 'MG - Apply'},  #rattan 3
    {'User': 'P2(P)', 'Start': 22.15, 'End': 22.18, 'Task': 'Color Texture'}, 
    {'User': 'P2(P)', 'Start': 22.19, 'End': 22.21, 'Task': 'Click Object'}, #Other 2 patio chair cushions
    # {'User': 'P2(P)', 'Start': 22.23, 'End': 22.30, 'Task': 'Scale Texture'}, 
    {'User': 'P2(P)', 'Start': 22.34, 'End': 22.41, 'Task': 'Click Object'}, # umbrella metals, patio chair frames, dining table, and dining chairs
    {'User': 'P2(P)', 'Start': 23.13, 'End': 23.48, 'Task': 'MG - Generate'}, #white metal
    {'User': 'P2(P)', 'Start': 23.56, 'End': 23.58, 'Task': 'MG - Brainstorm'}, #shiny, reflective, smooth
    {'User': 'P2(P)', 'Start': 24.06, 'End': 24.42, 'Task': 'MG - Generate'}, #white metal, shiny, reflective, smooth
    {'User': 'P2(P)', 'Start': 24.49, 'End': 24.49, 'Task': 'MG - Apply'}, #white metal, shiny, reflective, smooth 1
    {'User': 'P2(P)', 'Start': 25.03, 'End': 25.03, 'Task': 'Click Object'}, #Other umbrella canopy
    {'User': 'P2(P)', 'Start': 25.10, 'End': 25.46, 'Task': 'MG - Generate'}, #white metal, shiny, reflective, smooth
    {'User': 'P2(P)', 'Start': 25.52, 'End': 25.52, 'Task': 'MG - Apply'}, #green fabric 1
    {'User': 'P2(P)', 'Start': 26.03, 'End': 26.03, 'Task': 'Click Object'}, #Other sidetable
    {'User': 'P2(P)', 'Start': 26.13, 'End': 26.50, 'Task': 'MG - Generate'}, #wood
    {'User': 'P2(P)', 'Start': 26.55, 'End': 27.33, 'Task': 'MG - Generate'}, #wood, white
    # {'User': 'P2(P)', 'Start': 27.51, 'End': 27.53, 'Task': 'Rotate Texture'}, #90
    {'User': 'P2(P)', 'Start': 28.15, 'End': 29.42, 'Task': 'Render'}, 
    {'User': 'P2(P)', 'Start': 30.45, 'End': 30.54, 'Task': 'Save'}, 

    {'User': 'P3(P)', 'Start': 0.41, 'End': 0.50, 'Task': 'CB - Query Color'}, #Suggest color palettes that involve monochromatic blues.
    {'User': 'P3(P)', 'Start': 1.00, 'End': 1.00, 'Task': 'CB - Save Color'}, #Cool and Serene
    {'User': 'P3(P)', 'Start': 1.08, 'End': 1.10, 'Task': 'Click Object'}, #Fences
    {'User': 'P3(P)', 'Start': 1.38, 'End': 2.13, 'Task': 'MG - Generate'}, #white wood
    {'User': 'P3(P)', 'Start': 2.29, 'End': 2.29, 'Task': 'MG - Apply'}, #white wood 4
    {'User': 'P3(P)', 'Start': 3.37, 'End': 3.42, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P3(P)', 'Start': 4.10, 'End': 4.47, 'Task': 'MG - Generate'}, #leather
    # {'User': 'P3(P)', 'Start': 5.18, 'End': 5.18, 'Task': 'MG - Add Keyword'}, #matte
    {'User': 'P3(P)', 'Start': 5.25, 'End': 7.00, 'Task': 'MG - Generate'}, #leather, matte
    {'User': 'P3(P)', 'Start': 7.20, 'End': 7.20, 'Task': 'MG - Apply'}, #leather, matte 3
    # {'User': 'P3(P)', 'Start': 7.27, 'End': 7.48, 'Task': 'Scale Texture'}, #leather, matte 4
    {'User': 'P3(P)', 'Start': 8.28, 'End': 8.28, 'Task': 'Color Texture'}, #Cool and Serene 1
    {'User': 'P3(P)', 'Start': 8.48, 'End': 8.48, 'Task': 'Color Texture'}, #Cool and Serene 3
    {'User': 'P3(P)', 'Start': 9.16, 'End': 9.16, 'Task': 'Click Object'}, #both sidetables
    {'User': 'P3(P)', 'Start': 9.28, 'End': 10.57, 'Task': 'MG - Generate'}, #pine wood
    {'User': 'P3(P)', 'Start': 11.20, 'End': 11.20, 'Task': 'MG - Apply'}, #pine wood 10
    {'User': 'P3(P)', 'Start': 11.35, 'End': 11.40, 'Task': 'Color Texture'}, #white
    {'User': 'P3(P)', 'Start': 11.47, 'End': 11.54, 'Task': 'Color Texture'}, #white
    {'User': 'P3(P)', 'Start': 12.02, 'End': 12.02, 'Task': 'Click Object'}, #left sidetables
    {'User': 'P3(P)', 'Start': 12.57, 'End': 13.27, 'Task': 'CB - Query Material'}, #Suggest a material for an outdoor umbrella
    {'User': 'P3(P)', 'Start': 13.45, 'End': 15.17, 'Task': 'MG - Generate'}, #Olefin Fabric
    {'User': 'P3(P)', 'Start': 15.48, 'End': 17.18, 'Task': 'MG - Generate'}, #Generate Similar Olefin Fabric 3
    {'User': 'P3(P)', 'Start': 17.41, 'End': 17.41, 'Task': 'MG - Apply'}, #pine wood 10
    # {'User': 'P3(P)', 'Start': 17.50, 'End': 18.01, 'Task': 'Scale Texture'}, #leather, matte 4
    {'User': 'P3(P)', 'Start': 18.07, 'End': 18.07, 'Task': 'Click Object'}, #floor
    {'User': 'P3(P)', 'Start': 18.19, 'End': 19.50, 'Task': 'MG - Generate'}, #Wood planks
    {'User': 'P3(P)', 'Start': 20.15, 'End': 20.15, 'Task': 'MG - Apply'}, #wood planks 7
    # {'User': 'P3(P)', 'Start': 20.20, 'End': 20.49, 'Task': 'Scale Texture'}, #30
    {'User': 'P3(P)', 'Start': 20.57, 'End': 20.57, 'Task': 'Click Object'}, #pool edge
    # {'User': 'P3(P)', 'Start': 21.08, 'End': 21.08, 'Task': 'MG - Add Keyword'}, #glossy
    {'User': 'P3(P)', 'Start': 21.11, 'End': 22.40, 'Task': 'MG - Generate'}, #tiles, glossy
    {'User': 'P3(P)', 'Start': 22.56, 'End': 24.26, 'Task': 'MG - Generate'}, #tiles, glossy, white
    {'User': 'P3(P)', 'Start': 24.45, 'End': 24.45, 'Task': 'MG - Apply'}, #tiles, glossy, white 3
    {'User': 'P3(P)', 'Start': 25.03, 'End': 25.03, 'Task': 'Click Object'}, #pool edge
    {'User': 'P3(P)', 'Start': 25.30, 'End': 25.30, 'Task': 'Click Object'}, #patio chair frame
    {'User': 'P3(P)', 'Start': 25.46, 'End': 25.51, 'Task': 'MG - Brainstorm'}, 
    {'User': 'P3(P)', 'Start': 26.01, 'End': 26.07, 'Task': 'MG - Brainstorm'},
    {'User': 'P3(P)', 'Start': 26.13, 'End': 27.43, 'Task': 'MG - Generate'}, #metal, stainless
    {'User': 'P3(P)', 'Start': 28.37, 'End': 28.47, 'Task': 'Click Object'}, #all patio chair frames and umbrella poles
    {'User': 'P3(P)', 'Start': 29.05, 'End': 29.05, 'Task': 'MG - Apply'}, #metal 8
    # {'User': 'P3(P)', 'Start': 29.09, 'End': 29.13, 'Task': 'Set Metalness'}, # 1
    # {'User': 'P3(P)', 'Start': 29.24, 'End': 29.28, 'Task': 'Set Roughness'}, # 0.2
    # {'User': 'P3(P)', 'Start': 30.15, 'End': 27.43, 'Task': 'MG - Generate'}, #white wood
    {'User': 'P3(P)', 'Start': 31.09, 'End': 31.39, 'Task': 'Render'}, # 
    {'User': 'P3(P)', 'Start': 32.21, 'End': 32.31, 'Task': 'Save'}, 


    {'User': 'P4(P)', 'Start': 0.8, 'End': 0.8, 'Task': 'Click Object'}, #floor
    {'User': 'P4(P)', 'Start': 0.31, 'End': 1.58, 'Task': 'MG - Generate'}, #Blue tiles
    {'User': 'P4(P)', 'Start': 2.40, 'End': 2.40, 'Task': 'MG - Apply'}, #Blue tiles 2
    # Undo
    {'User': 'P4(P)', 'Start': 2.58, 'End': 2.58, 'Task': 'Click Object'}, #pool edge
    {'User': 'P4(P)', 'Start': 3.02, 'End': 3.02, 'Task': 'MG - Apply'}, #Blue tiles 2
    # {'User': 'P4(P)','Start': 3.17, 'End': 3.24, 'Task': 'Scale Texture'}, #5
    {'User': 'P4(P)', 'Start': 4.05, 'End': 4.05, 'Task': 'Click Object'}, #floor
    {'User': 'P4(P)', 'Start': 4.30, 'End': 5.57, 'Task': 'MG - Generate'}, #grey granite
    {'User': 'P4(P)', 'Start': 6.36, 'End': 8.03, 'Task': 'MG - Generate'}, #white granite, flooring
    {'User': 'P4(P)', 'Start': 8.28, 'End': 8.28, 'Task': 'MG - Apply'}, #white granite, flooring 10
    {'User': 'P4(P)', 'Start': 8.34, 'End': 8.39, 'Task': 'Color Texture'}, #grey
    # {'User': 'P4(P)', 'Start': 8.45, 'End': 8.52, 'Task': 'Scale Texture'}, #5
    {'User': 'P4(P)', 'Start': 9.04, 'End': 9.04, 'Task': 'Click Object'}, #floor
    # {'User': 'P4(P)', 'Start': 9.10, 'End': 9.13, 'Task': 'Scale Texture'}, #8
    {'User': 'P4(P)', 'Start': 9.58, 'End': 10.00, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P4(P)', 'Start': 10.32, 'End': 11.57, 'Task': 'MG - Generate'}, #plastic weaves
    {'User': 'P4(P)', 'Start': 12.22, 'End': 12.22, 'Task': 'MG - Apply'}, #plastic rattan 3
    {'User': 'P4(P)', 'Start': 12.33, 'End': 12.33, 'Task': 'Click Object'}, #patio chair cushions
    # {'User': 'P4(P)', 'Start': 12.35, 'End': 12.41, 'Task': 'Scale Texture'}, #10
    {'User': 'P4(P)', 'Start': 12.51, 'End': 12.51, 'Task': 'Click Object'}, #patio chair cushions
    # {'User': 'P4(P)', 'Start': 12.54, 'End': 12.56, 'Task': 'Scale Texture'}, #20
    {'User': 'P4(P)', 'Start': 13.39, 'End': 13.39, 'Task': 'Click Object'}, #patio chair frames
    {'User': 'P4(P)', 'Start': 13.58, 'End': 14.04, 'Task': 'Color Texture'}, #grey
    # {'User': 'P4(P)', 'Start': 14.07, 'End': 14.07, 'Task': 'Set Metalness'}, # 1
    # {'User': 'P4(P)', 'Start': 14.19, 'End': 14.19, 'Task': 'Set Roughness'}, # 0.6
    {'User': 'P4(P)', 'Start': 14.46, 'End': 14.46, 'Task': 'Click Object'}, #sidetables
    {'User': 'P4(P)', 'Start': 15.02, 'End': 15.02, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P4(P)', 'Start': 15.41, 'End': 17.04, 'Task': 'CB - Query Material'}, #Recommend coastliner fabric patterns
    {'User': 'P4(P)', 'Start': 17.46, 'End': 17.46, 'Task': 'CB - Apply'}, #Blue and white striped fabric
    # {'User': 'P4(P)', 'Start': 18.19, 'End': 18.19, 'Task': 'Rotate Texture'}, #0
    {'User': 'P4(P)', 'Start': 19.29, 'End': 19.26, 'Task': 'Click Object'}, #sofa chair frames
    {'User': 'P4(P)', 'Start': 19.33, 'End': 19.33, 'Task': 'CB - Apply'}, #Weather-resistant rattan furniture
    # {'User': 'P4(P)', 'Start': 19.43, 'End': 19.43, 'Task': 'Scale Texture'}, #20
    {'User': 'P4(P)', 'Start': 20.09, 'End': 20.09, 'Task': 'Click Object'}, #fences
    {'User': 'P4(P)', 'Start': 20.15, 'End': 20.15, 'Task': 'CB - Apply'}, #Light-colored wood decking
    {'User': 'P4(P)', 'Start': 20.47, 'End': 20.47, 'Task': 'Click Object'}, #fences
    {'User': 'P4(P)', 'Start': 21.03, 'End': 21.03, 'Task': 'Color Texture'}, #navy blue
    {'User': 'P4(P)', 'Start': 22.31, 'End': 22.44, 'Task': 'CB - Query Color'}, #Suggest color palettes for a coastline-inspired patio
    {'User': 'P4(P)', 'Start': 23.15, 'End': 23.15, 'Task': 'CB - Save Color'}, #Save Coastal Harmony color palette
    {'User': 'P4(P)', 'Start': 24.03, 'End': 24.03, 'Task': 'Color Texture'},
    {'User': 'P4(P)', 'Start': 24.44, 'End': 24.44, 'Task': 'Click Object'}, #sofa chair cushions
    {'User': 'P4(P)', 'Start': 25.02, 'End': 26.29, 'Task': 'MG - Generate'}, #water-resistant linen
    {'User': 'P4(P)', 'Start': 26.51, 'End': 26.51, 'Task': 'MG - Apply'}, #water-resistant linen 7
    {'User': 'P4(P)', 'Start': 27.21, 'End': 27.21, 'Task': 'Color Texture'},
    # {'User': 'P4(P)', 'Start': 28.24, 'End': 28.43, 'Task': 'CB - Query Material'}, #Suggest any Filipino material that can be useful for the coffee table
    # (Only 1 suggested material came out so she asked again.)
    {'User': 'P4(P)', 'Start': 29.20, 'End': 29.46, 'Task': 'CB - Query Material'}, #Suggest any Filipino materials that can be useful for the coffee table
    {'User': 'P4(P)', 'Start': 30.04, 'End': 30.04, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P4(P)', 'Start': 30.11, 'End': 30.11, 'Task': 'CB - Apply'}, #Wooden carvings
    {'User': 'P4(P)', 'Start': 31.23, 'End': 31.53, 'Task': 'Render'}, # 
    {'User': 'P4(P)', 'Start': 32.06, 'End': 32.16, 'Task': 'Save'}, 

    {'User': 'P5(S)', 'Start': 00.34, 'End': 1.32, 'Task': 'CB - Query Material'}, #I want to search a material for the fence
    {'User': 'P5(S)', 'Start': 2.27, 'End': 3.10, 'Task': 'CB - Query Material'}, #Can you suggest wood materials for the fence?
    {'User': 'P5(S)', 'Start': 3.30, 'End': 4.05, 'Task': 'CB-MG - Generate More'}, #Generate more Redwood
    {'User': 'P5(S)', 'Start': 4.15, 'End': 4.15, 'Task': 'Click Object'}, #fences
    {'User': 'P5(S)', 'Start': 4.17, 'End': 4.17, 'Task': 'MG - Apply'}, #redwood 3
    # {'User': 'P5(S)', 'Start': 4.35, 'End': 4.35, 'Task': 'Scale Texture'}, #4, 2.4
    {'User': 'P5(S)', 'Start': 4.59, 'End': 4.59, 'Task': 'Click Object'}, #floor
    {'User': 'P5(S)', 'Start': 5.07, 'End': 5.41, 'Task': 'MG - Generate'}, #tiles
    {'User': 'P5(S)', 'Start': 6.04, 'End': 6.04, 'Task': 'MG - Apply'}, #tiles 3
    # {'User': 'P5(S)', 'Start': 6.15, 'End': 6.15, 'Task': 'Scale Texture'}, #11
    {'User': 'P5(S)', 'Start': 6.40, 'End': 6.40, 'Task': 'Color Texture'}, #white
    # {'User': 'P5(S)', 'Start': 7.12, 'End': 7.12, 'Task': 'Set Roughness'}, #0.3
    {'User': 'P5(S)', 'Start': 7.44, 'End': 7.44, 'Task': 'Color Texture'}, #grey
    {'User': 'P5(S)', 'Start': 7.56, 'End': 7.56, 'Task': 'Click Object'}, #floor
    {'User': 'P5(S)', 'Start': 8.27, 'End': 9.53, 'Task': 'MG - Generate'}, #white tiles
    {'User': 'P5(S)', 'Start': 10.38, 'End': 10.38, 'Task': 'MG - Apply'}, #white tiles 10
    # {'User': 'P5(S)', 'Start': 11.05, 'End': 11.05, 'Task': 'Set Roughness'}, #0.9
    # {'User': 'P5(S)', 'Start': 11.15, 'End': 11.15, 'Task': 'Set Metalness'}, #0.3
    {'User': 'P5(S)', 'Start': 11.36, 'End': 11.36, 'Task': 'Color Texture'}, #light blue
    # {'User': 'P5(S)', 'Start': 11.58, 'End': 11.58, 'Task': 'Scale Texture'}, #8.0
    {'User': 'P5(S)', 'Start': 12.56, 'End': 12.56, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P5(S)', 'Start': 13.15, 'End': 13.15, 'Task': 'Color Texture'}, #light blue
    {'User': 'P5(S)', 'Start': 13.42, 'End': 13.42, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P5(S)', 'Start': 14.07, 'End': 14.07, 'Task': 'Color Texture'}, #white
    {'User': 'P5(S)', 'Start': 14.41, 'End': 16.09, 'Task': 'MG - Generate'}, #white fabric
    {'User': 'P5(S)', 'Start': 16.20, 'End': 16.20, 'Task': 'MG - Apply'}, #white fabric 3
    {'User': 'P5(S)', 'Start': 16.34, 'End': 16.34, 'Task': 'Click Object'}, #sofa chair cushions
    {'User': 'P5(S)', 'Start': 16.40, 'End': 16.40, 'Task': 'MG - Apply'}, #white fabric 3
    {'User': 'P5(S)', 'Start': 17.33, 'End': 19.02, 'Task': 'MG - Generate'}, #wood
    {'User': 'P5(S)', 'Start': 19.33, 'End': 19.33, 'Task': 'Click Object'}, #sidetables, coffee table, dining table, dining chairs
    {'User': 'P5(S)', 'Start': 20.25, 'End': 20.25, 'Task': 'MG - Apply'}, #wood 5
    {'User': 'P5(S)', 'Start': 20.41, 'End': 20.41, 'Task': 'Color Texture'}, #grey
    {'User': 'P5(S)', 'Start': 20.55, 'End': 20.55, 'Task': 'Click Object'}, #sidetables, coffee table, dining table, dining chairs
    {'User': 'P5(S)', 'Start': 21.12, 'End': 21.12, 'Task': 'Color Texture'}, #darker grey
    {'User': 'P5(S)', 'Start': 21.22, 'End': 21.22, 'Task': 'Click Object'}, #sidetables, coffee table, dining table, dining chairs
    {'User': 'P5(S)', 'Start': 21.34, 'End': 21.34, 'Task': 'Color Texture'}, #darker brown
    {'User': 'P5(S)', 'Start': 22.08, 'End': 22.08, 'Task': 'Click Object'}, #sofa chair frames
    {'User': 'P5(S)', 'Start': 22.12, 'End': 22.12, 'Task': 'MG - Apply'}, #wood 5
    {'User': 'P5(S)', 'Start': 22.23, 'End': 22.23, 'Task': 'Click Object'}, #coffee table top and sofa chair frames
    {'User': 'P5(S)', 'Start': 22.30, 'End': 22.30, 'Task': 'Color Texture'},
    {'User': 'P5(S)', 'Start': 22.55, 'End': 22.55, 'Task': 'Click Object'}, #sofa pillows
    # {'User': 'P5(S)', 'Start': 23.34, 'End': 23.53, 'Task': 'CB - Query Material'}, #what waterproof soft finishes are good for the pillows?
    #chatbot error
    {'User': 'P5(S)', 'Start': 24.11, 'End': 25.21, 'Task': 'CB - Query Material'}, #What waterproof textures are good for the pillows?
    {'User': 'P5(S)', 'Start': 25.43, 'End': 25.43, 'Task': 'Click Object'}, #sofa pillows and canopies
    {'User': 'P5(S)', 'Start': 25.50, 'End': 25.50, 'Task': 'CB - Apply'}, #nylon
    {'User': 'P5(S)', 'Start': 26.21, 'End': 26.21, 'Task': 'Color Texture'}, #light blue
    {'User': 'P5(S)', 'Start': 26.48, 'End': 26.48, 'Task': 'Click Object'}, #patio and umbrella frames
    {'User': 'P5(S)', 'Start': 27.07, 'End': 28.34, 'Task': 'MG - Generate'}, #steel
    {'User': 'P5(S)', 'Start': 29.07, 'End': 29.07, 'Task': 'MG - Apply'}, #steel 2
    {'User': 'P5(S)', 'Start': 29.13, 'End': 29.13, 'Task': 'Color Texture'}, #black
    {'User': 'P5(S)', 'Start': 29.29, 'End': 30.43, 'Task': 'Render'}, # 
    {'User': 'P5(S)', 'Start': 30.55, 'End': 31.06, 'Task': 'Save'}, 

    {'User': 'P6(S)', 'Start': 0.17, 'End': 0.17, 'Task': 'Click Object'}, #pool edge
    {'User': 'P6(S)', 'Start': 0.43, 'End': 1.37, 'Task': 'MG - Generate'}, #pool tiles
    {'User': 'P6(S)', 'Start': 1.56, 'End': 1.56, 'Task': 'MG - Apply'}, #pool tiles 1
    # {'User': 'P6(S)', 'Start': 2.23, 'End': 2.23, 'Task': 'Scale Texture'}, #17.7
    {'User': 'P6(S)', 'Start': 2.54, 'End': 2.54, 'Task': 'Click Object'}, #floor
    {'User': 'P6(S)', 'Start': 3.04, 'End': 4.04, 'Task': 'MG - Generate'}, #natural stone
    {'User': 'P6(S)', 'Start': 4.19, 'End': 4.19, 'Task': 'MG - Apply'}, #natural stone 2
    # {'User': 'P6(S)', 'Start': 4.3, 'End': 4.3, 'Task': 'Click Object'}, #floor. clicked but did nothing? maybe remove?
    {'User': 'P6(S)', 'Start': 5.05, 'End': 5.05, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P6(S)', 'Start': 5.18, 'End': 6.12, 'Task': 'MG - Generate'}, #chiffon
    {'User': 'P6(S)', 'Start': 6.58, 'End': 6.58, 'Task': 'MG - Apply'}, #chiffon 3
    # {'User': 'P6(S)', 'Start': 7.10, 'End': 7.10, 'Task': 'Set Roughness'}, #0.8
    {'User': 'P6(S)', 'Start': 7.57, 'End': 7.57, 'Task': 'Color Texture'}, #grey
    {'User': 'P6(S)', 'Start': 8.44, 'End': 9.36, 'Task': 'MG - Generate'}, #woven
    {'User': 'P6(S)', 'Start': 10.0, 'End': 10.0, 'Task': 'Click Object'}, #entire sofa and sofa chairs
    {'User': 'P6(S)', 'Start': 10.17, 'End': 10.17, 'Task': 'MG - Apply'}, #woven 5
    # {'User': 'P6(S)', 'Start': 10.31, 'End': 10.31, 'Task': 'Scale Texture'}, #7.1
    {'User': 'P6(S)', 'Start': 10.53, 'End': 10.53, 'Task': 'Click Object'}, #coffee table base
    {'User': 'P6(S)', 'Start': 11.0, 'End': 11.54, 'Task': 'MG - Generate'}, #wood
    {'User': 'P6(S)', 'Start': 12.20, 'End': 12.20, 'Task': 'MG - Apply'}, #wood 2
    {'User': 'P6(S)', 'Start': 12.40, 'End': 13.33, 'Task': 'MG - Generate'}, #glass
    {'User': 'P6(S)', 'Start': 13.45, 'End': 13.45, 'Task': 'MG - Brainstorm'}, #(none selected)
    {'User': 'P6(S)', 'Start': 13.45, 'End': 13.45, 'Task': 'MG - Add Keyword'}, #clear, transparent
    {'User': 'P6(S)', 'Start': 13.59, 'End': 14.52, 'Task': 'MG - Generate'}, #glass, clear, transparent
    {'User': 'P6(S)', 'Start': 15.14, 'End': 16.05, 'Task': 'MG - Generate'}, #glass, clear, transparent, smooth
    #set MG number to 10
    {'User': 'P6(S)', 'Start': 16.25, 'End': 17.57, 'Task': 'MG - Generate'}, #glass, clear, transparent, smooth
    {'User': 'P6(S)', 'Start': 18.24, 'End': 18.24, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P6(S)', 'Start': 19.21, 'End': 19.21, 'Task': 'MG - Apply'}, #glass 10
    # {'User': 'P6(S)', 'Start': 19.26, 'End': 19.26, 'Task': 'Set Opacity'}, #0.5
    {'User': 'P6(S)', 'Start': 19.56, 'End': 19.56, 'Task': 'Click Object'}, #sofa pillows
    {'User': 'P6(S)', 'Start': 20.02, 'End': 20.02, 'Task': 'Click Object'}, #sofa pillows
    {'User': 'P6(S)', 'Start': 21.45, 'End': 22.40, 'Task': 'MG - Generate'}, #canvas
    {'User': 'P6(S)', 'Start': 22.50, 'End': 23.44, 'Task': 'MG - Generate'}, #canvas, white
    {'User': 'P6(S)', 'Start': 24.10, 'End': 25.04, 'Task': 'MG - Generate'}, #fabric
    {'User': 'P6(S)', 'Start': 25.19, 'End': 25.19, 'Task': 'MG - Apply'}, #fabric 6
    {'User': 'P6(S)', 'Start': 25.47, 'End': 26.43, 'Task': 'MG - Generate'}, #fabric, white
    {'User': 'P6(S)', 'Start': 27.10, 'End': 27.10, 'Task': 'MG - Apply'}, #fabric 1
    {'User': 'P6(S)', 'Start': 27.24, 'End': 27.24, 'Task': 'Click Object'}, #left fence
    {'User': 'P6(S)', 'Start': 27.32, 'End': 28.30, 'Task': 'MG - Generate'}, #cypress wood
    {'User': 'P6(S)', 'Start': 28.42, 'End': 28.42, 'Task': 'Click Object'}, #right fence
    {'User': 'P6(S)', 'Start': 28.45, 'End': 28.45, 'Task': 'MG - Apply'}, #cypress wood 4
    {'User': 'P6(S)', 'Start': 28.55, 'End': 28.55, 'Task': 'Color Texture'}, #darker brown
    {'User': 'P6(S)', 'Start': 29.42, 'End': 29.42, 'Task': 'Click Object'}, #dining table
    {'User': 'P6(S)', 'Start': 30.01, 'End': 30.01, 'Task': 'MG - Apply'}, #cypress wood 6
    {'User': 'P6(S)', 'Start': 30.21, 'End': 31.13, 'Task': 'MG - Generate'}, #acacia wood
    {'User': 'P6(S)', 'Start': 31.31, 'End': 31.31, 'Task': 'Click Object'}, #dining chairs
    {'User': 'P6(S)', 'Start': 31.37, 'End': 31.37, 'Task': 'MG - Apply'}, #acacia wood 1
    {'User': 'P6(S)', 'Start': 32.20, 'End': 32.50, 'Task': 'Render'}, 
    {'User': 'P6(S)', 'Start': 33.15, 'End': 33.30, 'Task': 'Save'}, 

    {'User': 'P7(P)', 'Start': 0.10, 'End': 0.45, 'Task': 'MG - Generate'}, #sandstone flooring
    {'User': 'P7(P)', 'Start': 0.48, 'End': 0.48, 'Task': 'Click Object'}, #floor
    {'User': 'P7(P)', 'Start': 0.51, 'End': 0.51, 'Task': 'MG - Apply'}, #sandstone flooring 4
    # {'User': 'P7(P)', 'Start': 0.59, 'End': 0.59, 'Task': 'Scale Texture'}, #2.4
    {'User': 'P7(P)', 'Start': 1.16, 'End': 1.51, 'Task': 'MG - Generate'}, #stucco wall
    {'User': 'P7(P)', 'Start': 2.01, 'End': 2.01, 'Task': 'Click Object'}, #fences
    {'User': 'P7(P)', 'Start': 2.04, 'End': 2.04, 'Task': 'MG - Apply'}, #stucco wall 1
    {'User': 'P7(P)', 'Start': 2.16, 'End': 2.16, 'Task': 'Color Texture'}, #cream yellow
    {'User': 'P7(P)', 'Start': 2.30, 'End': 3.07, 'Task': 'MG - Generate'}, #white rattan
    {'User': 'P7(P)', 'Start': 3.24, 'End': 3.24, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 3.27, 'End': 3.27, 'Task': 'MG - Apply'}, #white rattan 2
    {'User': 'P7(P)', 'Start': 3.30, 'End': 3.30, 'Task': 'MG - Apply'}, #white rattan 4
    # {'User': 'P7(P)', 'Start': 3.35, 'End': 3.35, 'Task': 'Scale Texture'}, #3.9
    {'User': 'P7(P)', 'Start': 4.05, 'End': 4.42, 'Task': 'MG - Generate'}, #white wood wash
    {'User': 'P7(P)', 'Start': 4.25, 'End': 4.25, 'Task': 'Click Object'}, #floor
    {'User': 'P7(P)', 'Start': 4.45, 'End': 4.45, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 4.48, 'End': 4.48, 'Task': 'Click Object'}, #coffee table base
    {'User': 'P7(P)', 'Start': 4.51, 'End': 4.51, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 4.57, 'End': 4.57, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 5.05, 'End': 5.05, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 5.14, 'End': 5.14, 'Task': 'Click Object'}, #sofa chair frames
    {'User': 'P7(P)', 'Start': 5.17, 'End': 5.17, 'Task': 'MG - Apply'}, #white wood wash 2
    {'User': 'P7(P)', 'Start': 5.29, 'End': 5.29, 'Task': 'Color Texture'}, #yellow
    {'User': 'P7(P)', 'Start': 5.38, 'End': 5.38, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 5.45, 'End': 5.45, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 5.54, 'End': 5.54, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P7(P)', 'Start': 5.57, 'End': 5.57, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 6.00, 'End': 6.00, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P7(P)', 'Start': 6.01, 'End': 6.01, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 6.45, 'End': 6.45, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P7(P)', 'Start': 6.48, 'End': 6.48, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 6.45, 'End': 6.45, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 6.55, 'End': 6.55, 'Task': 'Color Texture'}, #dark grey
    {'User': 'P7(P)', 'Start': 7.00, 'End': 7.00, 'Task': 'Color Texture'}, #light grey
    {'User': 'P7(P)', 'Start': 7.10, 'End': 7.10, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 7.12, 'End': 7.12, 'Task': 'Color Texture'}, #grey
    {'User': 'P7(P)', 'Start': 7.23, 'End': 7.23, 'Task': 'Click Object'}, #sofa chair frame
    # {'User': 'P7(P)', 'Start': 7.25, 'End': 7.25, 'Task': 'Set Roughness'}, #0.6
    {'User': 'P7(P)', 'Start': 8.04, 'End': 8.04, 'Task': 'Click Object'}, #dining table (took long, had a hard time)
    {'User': 'P7(P)', 'Start': 8.45, 'End': 8.45, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 9.03, 'End': 9.03, 'Task': 'Click Object'}, #side table
    {'User': 'P7(P)', 'Start': 9.05, 'End': 9.05, 'Task': 'MG - Apply'}, #white wood wash 1
    {'User': 'P7(P)', 'Start': 9.19, 'End': 9.19, 'Task': 'Click Object'}, #sofa chair frames and others
    # was scrolling back and forth the objects selected??
    {'User': 'P7(P)', 'Start': 10.40, 'End': 10.40, 'Task': 'Color Texture'}, #green??
    {'User': 'P7(P)', 'Start': 11.08, 'End': 11.08, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 11.15, 'End': 11.15, 'Task': 'Click Object'}, #other sofa chair frames
    {'User': 'P7(P)', 'Start': 11.27, 'End': 11.27, 'Task': 'Color Texture'}, #pink (??)
    {'User': 'P7(P)', 'Start': 11.50, 'End': 11.50, 'Task': 'Click Object'}, #other sofa chair frame
    {'User': 'P7(P)', 'Start': 11.52, 'End': 11.52, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 12.02, 'End': 12.02, 'Task': 'Click Object'}, #other sofa chair frame that's pink
    {'User': 'P7(P)', 'Start': 12.04, 'End': 12.04, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 12.17, 'End': 12.17, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P7(P)', 'Start': 12.19, 'End': 12.19, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 12.23, 'End': 12.23, 'Task': 'Click Object'}, #coffee table base
    {'User': 'P7(P)', 'Start': 12.25, 'End': 12.25, 'Task': 'Color Texture'}, #grey
    {'User': 'P7(P)', 'Start': 12.35, 'End': 12.35, 'Task': 'Click Object'}, #sofa cushions
    {'User': 'P7(P)', 'Start': 12.44, 'End': 13.18, 'Task': 'MG - Generate'}, #blue white stripes
    {'User': 'P7(P)', 'Start': 12.58, 'End': 12.58, 'Task': 'Click Object'}, #sidetable
    {'User': 'P7(P)', 'Start': 13.03, 'End': 13.03, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 13.12, 'End': 13.12, 'Task': 'Click Object'}, #sidetable
    {'User': 'P7(P)', 'Start': 13.14, 'End': 13.14, 'Task': 'Color Texture'}, #beige
    {'User': 'P7(P)', 'Start': 13.45, 'End': 14.20, 'Task': 'MG - Generate'}, #blue white stripes, solid stripe, modern, streamline
    {'User': 'P7(P)', 'Start': 14.25, 'End': 14.25, 'Task': 'Click Object'}, #sofa cushions
    {'User': 'P7(P)', 'Start': 14.27, 'End': 14.27, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 3
    {'User': 'P7(P)', 'Start': 14.41, 'End': 15.09, 'Task': 'MG - Generate'}, #blue white stripes, solid stripe, modern, streamline (similar textures to 3)
    # set number 10
    {'User': 'P7(P)', 'Start': 15.16, 'End': 16.40, 'Task': 'MG - Generate'}, #blue white stripes, solid stripe, modern, streamline 
    {'User': 'P7(P)', 'Start': 16.18, 'End': 16.18, 'Task': 'Click Object'}, #sofa cushion
    # {'User': 'P7(P)', 'Start': 16.25, 'End': 16.25, 'Task': 'Rotate Texture'}, #57 (i think playing around while waiting)
    {'User': 'P7(P)', 'Start': 16.26, 'End': 16.26, 'Task': 'Click Object'}, #sofa cushion
    {'User': 'P7(P)', 'Start': 16.47, 'End': 16.47, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 16.49, 'End': 16.49, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 16.50, 'End': 16.50, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 16.55, 'End': 16.55, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 16.57, 'End': 16.57, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.01, 'End': 17.01, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 2
    {'User': 'P7(P)', 'Start': 17.05, 'End': 17.05, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.06, 'End': 17.06, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.07, 'End': 17.07, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.09, 'End': 17.09, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.13, 'End': 17.13, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.14, 'End': 17.14, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.18, 'End': 17.18, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.19, 'End': 17.19, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.21, 'End': 17.21, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.22, 'End': 17.22, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.28, 'End': 17.28, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.30, 'End': 17.30, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.34, 'End': 17.34, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.35, 'End': 17.35, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 17.37, 'End': 17.37, 'Task': 'Click Object'}, #another sofa cushion
    {'User': 'P7(P)', 'Start': 17.39, 'End': 17.39, 'Task': 'MG - Apply'}, #blue white stripes, solid stripe, modern, streamline 7
    {'User': 'P7(P)', 'Start': 18.0, 'End': 18.30, 'Task': 'Render'}, 
    {'User': 'P7(P)', 'Start': 19.30, 'End': 19.45, 'Task': 'Save'}, 

    {'User': 'P8(P)', 'Start': 0.34, 'End': 1.23, 'Task': 'CB - Query Material'}, #what are your suggestions for poolside flooring
    {'User': 'P8(P)', 'Start': 2.00, 'End': 2.00, 'Task': 'Click Object'}, #floor
    {'User': 'P8(P)', 'Start': 2.17, 'End': 2.17, 'Task': 'CB - Apply'}, #ceramic tile flooring
    # {'User': 'P8(P)', 'Start': 2.25, 'End': 2.25, 'Task': 'Scale Texture'}, #11.5
    {'User': 'P8(P)', 'Start': 2.43, 'End': 2.43, 'Task': 'Color Texture'}, #yellow beige
    {'User': 'P8(P)', 'Start': 3.18, 'End': 4.23, 'Task': 'CB - Query Material'}, #suggest pool flooring materials
    {'User': 'P8(P)', 'Start': 5.02, 'End': 5.02, 'Task': 'Click Object'}, #pool edge
    {'User': 'P8(P)', 'Start': 5.04, 'End': 5.04, 'Task': 'CB - Apply'}, #porcelain tiles
    # {'User': 'P8(P)', 'Start': 5.16, 'End': 5.16, 'Task': 'Scale Texture'}, #8.5
    {'User': 'P8(P)', 'Start': 5.52, 'End': 6.54, 'Task': 'CB - Query Material'}, #umbrella materials suggestions
    {'User': 'P8(P)', 'Start': 7.25, 'End': 7.25, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P8(P)', 'Start': 7.30, 'End': 8.15, 'Task': 'CB-MG - Generate More'}, #polyster fabric umbrellas (generate more)
    {'User': 'P8(P)', 'Start': 7.32, 'End': 7.32, 'Task': 'CB - Apply'}, #polyster fabric umbrellas
    {'User': 'P8(P)', 'Start': 7.40, 'End': 7.40, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P8(P)', 'Start': 7.57, 'End': 7.57, 'Task': 'Color Texture'}, #navy blue
    {'User': 'P8(P)', 'Start': 8.21, 'End': 8.21, 'Task': 'Click Object'}, #sidetables
    {'User': 'P8(P)', 'Start': 8.53, 'End': 9.30, 'Task': 'MG - Generate'}, #woven material
    {'User': 'P8(P)', 'Start': 9.32, 'End': 10.09, 'Task': 'MG - Generate'}, #woven material, borwn, natural, light
    {'User': 'P8(P)', 'Start': 10.21, 'End': 10.21, 'Task': 'MG - Apply'}, #woven material 1
    {'User': 'P8(P)', 'Start': 10.47, 'End': 11.25, 'Task': 'CB - Query Material'}, # beach bed material suggestions
    {'User': 'P8(P)', 'Start': 12.04, 'End': 12.41, 'Task': 'MG - Generate'}, #cotton fabric, light
    {'User': 'P8(P)', 'Start': 12.58, 'End': 12.58, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P8(P)', 'Start': 13.02, 'End': 13.02, 'Task': 'MG - Apply'}, #cotton fabric 3
    {'User': 'P8(P)', 'Start': 13.34, 'End': 13.34, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P8(P)', 'Start': 13.42, 'End': 13.42, 'Task': 'Color Texture'}, #cream brown
    {'User': 'P8(P)', 'Start': 15.10, 'End': 16.07, 'Task': 'CB - Query Material'}, #outdoor sofa material suggestions
    {'User': 'P8(P)', 'Start': 16.38, 'End': 16.38, 'Task': 'Click Object'}, #sofa chair frames
    {'User': 'P8(P)', 'Start': 16.50, 'End': 16.50, 'Task': 'CB - Apply'}, #Woven wicker or rattan frame with cushions
    # {'User': 'P8(P)', 'Start': 17.01, 'End': 17.01, 'Task': 'Scale Texture'}, #1.0
    # {'User': 'P8(P)', 'Start': 17.32, 'End': 17.32, 'Task': 'Set Roughness'}, #0.8
    {'User': 'P8(P)', 'Start': 18.02, 'End': 18.47, 'Task': 'MG - Generate'}, #canvas fabric, light
    {'User': 'P8(P)', 'Start': 18.49, 'End': 18.49, 'Task': 'Click Object'}, #sofa chair cushions and pillows
    {'User': 'P8(P)', 'Start': 19.00, 'End': 19.00, 'Task': 'MG - Apply'}, #cotton fabric 3
    {'User': 'P8(P)', 'Start': 19.10, 'End': 19.10, 'Task': 'Click Object'}, #sofa chair cushions
    # {'User': 'P8(P)', 'Start': 19.14, 'End': 19.14, 'Task': 'Scale Texture'}, #11.5
    {'User': 'P8(P)', 'Start': 19.50, 'End': 19.50, 'Task': 'Color Texture'}, #grey
    {'User': 'P8(P)', 'Start': 19.55, 'End': 19.55, 'Task': 'Click Object'}, #sofa chair cushions
    {'User': 'P8(P)', 'Start': 19.57, 'End': 19.57, 'Task': 'Color Texture'}, #dark grey
    {'User': 'P8(P)', 'Start': 20.35, 'End': 20.35, 'Task': 'Click Object'}, #left 3 pillows
    {'User': 'P8(P)', 'Start': 20.39, 'End': 20.39, 'Task': 'Color Texture'}, #olive green
    {'User': 'P8(P)', 'Start': 21.08, 'End': 21.08, 'Task': 'Click Object'}, #right 3 pillows
    {'User': 'P8(P)', 'Start': 21.15, 'End': 21.15, 'Task': 'Color Texture'}, #light green
    {'User': 'P8(P)', 'Start': 21.58, 'End': 21.58, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P8(P)', 'Start': 22.34, 'End': 23.13, 'Task': 'MG - Generate'}, #glass, light, smooth, fine, clear
    {'User': 'P8(P)', 'Start': 23.31, 'End': 23.31, 'Task': 'MG - Apply'}, #glass, light, smooth, fine, clear 2
    # {'User': 'P8(P)', 'Start': 23.40, 'End': 23.40, 'Task': 'Scale Texture'}, #1.0
    {'User': 'P8(P)', 'Start': 24.06, 'End': 24.06, 'Task': 'Color Texture'}, #light blue
    # {'User': 'P8(P)', 'Start': 24.22, 'End': 24.22, 'Task': 'Set Opacity'}, #0.4
    # {'User': 'P8(P)', 'Start': 24.35, 'End': 24.35, 'Task': 'Set Roughness'}, #0.2
    {'User': 'P8(P)', 'Start': 25.19, 'End': 25.56, 'Task': 'MG - Generate'}, # oak wood, light, smooth, fine, natural
    {'User': 'P8(P)', 'Start': 26.10, 'End': 26.10, 'Task': 'Click Object'}, #coffee table base
    {'User': 'P8(P)', 'Start': 26.12, 'End': 26.12, 'Task': 'MG - Apply'}, #oak wood, light, smooth, fine, natural 4
    {'User': 'P8(P)', 'Start': 26.45, 'End': 26.45, 'Task': 'Click Object'}, #dining table top
    {'User': 'P8(P)', 'Start': 27.04, 'End': 27.38, 'Task': 'MG - Generate'}, # glass, light, smooth, fine, clear
    {'User': 'P8(P)', 'Start': 27.55, 'End': 27.55, 'Task': 'MG - Apply'}, #glass, light, smooth, fine, clear 1
    # {'User': 'P8(P)', 'Start': 28.0, 'End': 28.0, 'Task': 'Scale Texture'}, #6.7
    {'User': 'P8(P)', 'Start': 28.18, 'End': 28.18, 'Task': 'Color Texture'}, #light blue
    # {'User': 'P8(P)', 'Start': 28.30, 'End': 28.30, 'Task': 'Set Roughness'}, #0.1
    {'User': 'P8(P)', 'Start': 29.19, 'End': 30.31, 'Task': 'MG - Generate'}, # wood finish, light, smooth, fine
    # Set number 8
    {'User': 'P8(P)', 'Start': 30.50, 'End': 30.50, 'Task': 'MG - Apply'}, #wood finish, light, smooth, fine 3
    {'User': 'P8(P)', 'Start': 31.08, 'End': 31.08, 'Task': 'Click Object'}, #dining chairs
    {'User': 'P8(P)', 'Start': 31.20, 'End': 31.20, 'Task': 'MG - Apply'}, #wood finish, light, smooth, fine 3
    {'User': 'P8(P)', 'Start': 31.37, 'End': 32.27, 'Task': 'Render'}, 
    {'User': 'P8(P)', 'Start': 32.55, 'End': 33.10, 'Task': 'Save'}, 


    {'User': 'P9(S)', 'Start': 0.11, 'End': 0.56, 'Task': 'MG - Generate'}, #sandstone
    {'User': 'P9(S)', 'Start': 0.15, 'End': 0.15, 'Task': 'Click Object'}, #floor
    {'User': 'P9(S)', 'Start': 1.04, 'End': 1.27, 'Task': 'CB - Query Material'}, # materials for outdoor chair upholstery (error came out)
    # Add keywords
    {'User': 'P9(S)', 'Start': 1.12, 'End': 1.12, 'Task': 'MG - Add Keyword'}, #light colored, beige, sand like
    {'User': 'P9(S)', 'Start': 1.29, 'End': 2.04, 'Task': 'MG - Generate'}, #sandstone, light colored, beige, sand like
    {'User': 'P9(S)', 'Start': 1.48, 'End': 2.11, 'Task': 'CB - Query Material'}, # materials for outdoor chair upholstery (error came out)
    {'User': 'P9(S)', 'Start': 2.08, 'End': 2.08, 'Task': 'MG - Apply'}, #sandstone, light colored, beige, sand like 2
    {'User': 'P9(S)', 'Start': 2.31, 'End': 3.07, 'Task': 'MG - Generate'}, #polyester, light colored, beige, sand like
    {'User': 'P9(S)', 'Start': 2.37, 'End': 2.37, 'Task': 'Click Object'}, #patio chair cushions
    {'User': 'P9(S)', 'Start': 2.08, 'End': 2.08, 'Task': 'MG - Apply'}, #polyester, light colored, beige, sand like 2
    {'User': 'P9(S)', 'Start': 3.21, 'End': 4.06, 'Task': 'MG - Generate'}, #polyester
    {'User': 'P9(S)', 'Start': 3.33, 'End': 3.33, 'Task': 'CB - Apply'}, # sunbrella fabric
    #(she applied to all parts by accident and wnated to remove from the metal frame)
    {'User': 'P9(S)', 'Start': 4.19, 'End': 4.28, 'Task': 'MG - Generate'}, #polyester fabric
    {'User': 'P9(S)', 'Start': 4.28, 'End': 4.52, 'Task': 'MG - Generate'}, #Sunbrella Fabric (from CB)
    {'User': 'P9(S)', 'Start': 4.40, 'End': 4.40, 'Task': 'Click Object'}, #floor
    {'User': 'P9(S)', 'Start': 5.22, 'End': 4.52, 'Task': 'MG - Generate'}, #stainless steel, smooth
    {'User': 'P9(S)', 'Start': 5.50, 'End': 5.50, 'Task': 'Click Object'}, #patio chair cushions
    # {'User': 'P9(S)', 'Start': 6.00, 'End': 6.00, 'Task': 'Scale Texture'}, #1.8
    {'User': 'P9(S)', 'Start': 5.50, 'End': 5.50, 'Task': 'Click Object'}, #patio chair cushions
    # {'User': 'P9(S)', 'Start': 6.08, 'End': 6.08, 'Task': 'Scale Texture'}, #1.0
    # {'User': 'P9(S)', 'Start': 6.10, 'End': 6.10, 'Task': 'Translate Texture'}, #0.4
    {'User': 'P9(S)', 'Start': 6.27, 'End': 6.27, 'Task': 'Click Object'}, #patio chair frames
    {'User': 'P9(S)', 'Start': 6.39, 'End': 6.39, 'Task': 'MG - Apply'}, #stainless steel, smooth 3
    # Set to 10
    {'User': 'P9(S)', 'Start': 7.22, 'End': 8.49, 'Task': 'MG - Generate'}, #tiles, smooth
    {'User': 'P9(S)', 'Start': 8.00, 'End': 8.00, 'Task': 'Click Object'}, #pool edge
    {'User': 'P9(S)', 'Start': 9.06, 'End': 10.33, 'Task': 'MG - Generate'}, # generate similar tiles, smooth 3
    {'User': 'P9(S)', 'Start': 10.41, 'End': 10.41, 'Task': 'MG - Apply'}, #tiles 1
    {'User': 'P9(S)', 'Start': 10.46, 'End': 10.46, 'Task': 'Color Texture'}, #light blue
    {'User': 'P9(S)', 'Start': 11.22, 'End': 12.50, 'Task': 'MG - Generate'}, # poly cotton, smooth, white
    {'User': 'P9(S)', 'Start': 12.58, 'End': 12.58, 'Task': 'Click Object'}, #patio seat cushions
    {'User': 'P9(S)', 'Start': 13.13, 'End': 13.13, 'Task': 'MG - Apply'}, #poly cotton 1
    {'User': 'P9(S)', 'Start': 14.15, 'End': 14.15, 'Task': 'Click Object'}, #sofa chairs
    {'User': 'P9(S)', 'Start': 14.23, 'End': 14.23, 'Task': 'MG - Apply'}, #poly cotton 1
    {'User': 'P9(S)', 'Start': 15.15, 'End': 15.15, 'Task': 'Click Object'}, #sofa chair frames
    {'User': 'P9(S)', 'Start': 14.33, 'End': 15.18, 'Task': 'CB-MG - Generate More'}, # Generate more synthetic resin wicker (CB)
    {'User': 'P9(S)', 'Start': 15.24, 'End': 15.24, 'Task': 'MG - Apply'}, #synthetic resin wicker 1
    # {'User': 'P9(S)', 'Start': 15.28, 'End': 15.28, 'Task': 'Scale Texture'}, #5
    {'User': 'P9(S)', 'Start': 16.15, 'End': 17.00, 'Task': 'MG - Generate'}, # Generate oak wood, light colored
    {'User': 'P9(S)', 'Start': 17.13, 'End': 17.13, 'Task': 'Click Object'}, #tabletop frame and dining chairs
    {'User': 'P9(S)', 'Start': 17.23, 'End': 17.23, 'Task': 'MG - Apply'}, #oak wood 4
    {'User': 'P9(S)', 'Start': 18.17, 'End': 18.17, 'Task': 'Click Object'}, #table frame
    {'User': 'P9(S)', 'Start': 18.26, 'End': 18.26, 'Task': 'MG - Apply'}, #oak wood 4
    {'User': 'P9(S)', 'Start': 18.30, 'End': 18.30, 'Task': 'Click Object'}, #coffee tabletop
    {'User': 'P9(S)', 'Start': 18.33, 'End': 18.33, 'Task': 'MG - Apply'}, #oak wood 4
    {'User': 'P9(S)', 'Start': 18.38, 'End': 18.38, 'Task': 'Click Object'}, #sofa frames
    {'User': 'P9(S)', 'Start': 19.06, 'End': 19.50, 'Task': 'MG - Generate'}, #Synthetic Resin Wicker, light colored
    {'User': 'P9(S)', 'Start': 19.55, 'End': 19.55, 'Task': 'MG - Apply'}, #Synthetic Resin Wicker, light colored 4
    {'User': 'P9(S)', 'Start': 20.13, 'End': 20.13, 'Task': 'Click Object'}, #sofa frames
    {'User': 'P9(S)', 'Start': 20.22, 'End': 20.22, 'Task': 'MG - Apply'}, #Synthetic Resin Wicker, light colored 2
    {'User': 'P9(S)', 'Start': 20.40, 'End': 21.00, 'Task': 'CB - Query Material'}, # wood for fence
    {'User': 'P9(S)', 'Start': 21.10, 'End': 21.30, 'Task': 'CB-MG - Generate More'}, #Generate more cedar
    {'User': 'P9(S)', 'Start': 21.30, 'End': 21.53, 'Task': 'MG - Generate'}, #Generate cedar wood
    {'User': 'P9(S)', 'Start': 22.15, 'End': 22.15, 'Task': 'Click Object'}, #fences
    {'User': 'P9(S)', 'Start': 22.20, 'End': 23.30, 'Task': 'Render'}, 
    {'User': 'P9(S)', 'Start': 22.43, 'End': 23.03, 'Task': 'CB - Query Material'}, # material for sunshade umbrella
    {'User': 'P9(S)', 'Start': 23.23, 'End': 24.10, 'Task': 'CB-MG - Generate More'}, #Generate more sunbrella shade fabrics (CB)
    {'User': 'P9(S)', 'Start': 24.15, 'End': 24.15, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P9(S)', 'Start': 24.22, 'End': 24.22, 'Task': 'MG - Apply'}, #sunbrella shade fabrics 4
    {'User': 'P9(S)', 'Start': 24.32, 'End': 25.14, 'Task': 'MG - Generate'}, #blue tiles
    {'User': 'P9(S)', 'Start': 25.28, 'End': 25.28, 'Task': 'Click Object'}, #pool edge
    {'User': 'P9(S)', 'Start': 25.30, 'End': 25.30, 'Task': 'MG - Apply'}, #blue tiles 3
    {'User': 'P9(S)', 'Start': 25.33, 'End': 25.33, 'Task': 'MG - Apply'}, #blue tiles 1
    {'User': 'P9(S)', 'Start': 25.37, 'End': 25.37, 'Task': 'MG - Apply'}, #blue tiles 4
    # {'User': 'P9(S)', 'Start': 25.53, 'End': 25.53, 'Task': 'Scale Texture'}, #4.7
    {'User': 'P9(S)', 'Start': 26.34, 'End': 27.41, 'Task': 'Render'}, 
    {'User': 'P9(S)', 'Start': 28.28, 'End': 28.39, 'Task': 'Save'}, 

    {'User': 'P10(S)', 'Start': 0.07, 'End': 0.07, 'Task': 'Click Object'}, #click pool edge
    {'User': 'P10(S)', 'Start': 0.50, 'End': 2.24, 'Task': 'MG - Generate'}, # blue subway tiles
    # Set number to 10
    {'User': 'P10(S)', 'Start': 1.21, 'End': 2.10, 'Task': 'CB - Query Material'}, #outdoor materials for furniture
    # "I have a question, is there any pre-saved materials?"
    {'User': 'P10(S)', 'Start': 2.55, 'End': 2.55, 'Task': 'MG - Apply'}, #blue subway tiles 9
    # {'User': 'P10(S)', 'Start': 3.21, 'End': 3.21, 'Task': 'Scale Texture'}, #9.2
    # "I was thinking that it would suggest rattan?"
    {'User': 'P10(S)', 'Start': 4.35, 'End': 6.05, 'Task': 'MG - Generate'}, #rattan
    {'User': 'P10(S)', 'Start': 5.20, 'End': 6.45, 'Task': 'CB - Query Material'}, #suggest wood decking material
    {'User': 'P10(S)', 'Start': 6.17, 'End': 7.49, 'Task': 'MG - Generate'}, #white woven rattan
    {'User': 'P10(S)', 'Start': 8.30, 'End': 8.30, 'Task': 'Click Object'}, #coffee table top 
    {'User': 'P10(S)', 'Start': 8.35, 'End': 8.35, 'Task': 'Click Object'}, #coffee table base
    {'User': 'P10(S)', 'Start': 8.37, 'End': 8.37, 'Task': 'MG - Apply'}, #white woven rattan
    {'User': 'P10(S)', 'Start': 8.40, 'End': 8.40, 'Task': 'Click Object'}, #coffee table base 8 
    {'User': 'P10(S)', 'Start': 9.13, 'End': 9.13, 'Task': 'Click Object'}, # dining table top
    {'User': 'P10(S)', 'Start': 9.17, 'End': 9.17, 'Task': 'Click Object'}, # dining table frame
    {'User': 'P10(S)', 'Start': 9.30, 'End': 9.30, 'Task': 'Click Object'}, # sidetables
    {'User': 'P10(S)', 'Start': 9.40, 'End': 9.40, 'Task': 'MG - Apply'}, #white woven rattan 8 
    # {'User': 'P10(S)', 'Start': 9.57, 'End': 9.57, 'Task': 'Scale Texture'}, #4.7
    # {'User': 'P10(S)', 'Start': 11.16, 'End': 11.16, 'Task': 'MG - Add Keyword'}, #tempered
    {'User': 'P10(S)', 'Start': 11.23, 'End': 11.23, 'Task': 'MG - Brainstorm'}, #transparent, clear
    {'User': 'P10(S)', 'Start': 12.16, 'End': 13.47, 'Task': 'MG - Generate'}, #glass, tempered, transparent, clear
    # "can you generate more? I'm looking for glass that is clear"
    # {'User': 'P10(S)', 'Start': , 'End': , 'Task': 'MG - Add Keyword'}, #smooth
    {'User': 'P10(S)', 'Start': 14.53, 'End': 16.34, 'Task': 'MG - Generate'},#glass, tempered, transparent, clear, smooth
    {'User': 'P10(S)', 'Start': 15.23, 'End': 16.16, 'Task': 'CB - Query Color'}, #suggest colors for coastal design (error)
    {'User': 'P10(S)', 'Start': 16.45, 'End': 17.02, 'Task': 'CB - Query Color'}, #suggest colors for coastal design (error)
    {'User': 'P10(S)', 'Start': 17.04, 'End': 17.04, 'Task': 'Click Object'}, # coffee table top
    {'User': 'P10(S)', 'Start': 17.08, 'End': 17.08, 'Task': 'MG - Apply'}, #glass, tempered, transparent, clear, smooth 5
    {'User': 'P10(S)', 'Start': 17.18, 'End': 17.18, 'Task': 'Click Object'}, # coffee table top
    # {'User': 'P10(S)', 'Start': 17.22, 'End': 17.22, 'Task': 'Set Opacity'}, #0.3
    {'User': 'P10(S)', 'Start': 17.48, 'End': 17.48, 'Task': 'Click Object'}, # dining table top
    {'User': 'P10(S)', 'Start': 17.53, 'End': 17.53, 'Task': 'MG - Apply'}, #glass, tempered, transparent, clear, smooth 5
    # {'User': 'P10(S)', 'Start': 17.57, 'End': 17.57, 'Task': 'Set Opacity'}, #0.3
    {'User': 'P10(S)', 'Start': 18.16, 'End': 19.10, 'Task': 'CB - Query Color'}, #suggest colors for coastal design
    {'User': 'P10(S)', 'Start': 18.48, 'End': 19.45, 'Task': 'MG - Generate'}, #white oak
    {'User': 'P10(S)', 'Start': 19.48, 'End': 19.48, 'Task': 'CB - Save Color'},#Soft Green
    {'User': 'P10(S)', 'Start': 20.02, 'End': 20.02, 'Task': 'Click Object'}, # sofa cushions
    {'User': 'P10(S)', 'Start': 20.34, 'End': 20.34, 'Task': 'Click Object'}, # sofa cushions
    {'User': 'P10(S)', 'Start': 20.47, 'End': 20.47, 'Task': 'Color Texture'}, # Soft Green 4
    {'User': 'P10(S)', 'Start': 21.20, 'End': 21.20, 'Task': 'Click Object'}, # patio chair cushions
    {'User': 'P10(S)', 'Start': 21.32, 'End': 21.32, 'Task': 'Color Texture'}, # Soft Green 3
    # {'User': 'P10(S)', 'Start': , 'End': , 'Task': 'MG - Apply'}, #white oak (??)
    {'User': 'P10(S)', 'Start': 22.15, 'End': 22.15, 'Task': 'Click Object'}, # dining table frame
    {'User': 'P10(S)', 'Start': 22.17, 'End': 22.17, 'Task': 'MG - Apply'}, #white oak (??)
    {'User': 'P10(S)', 'Start': 22.42, 'End': 27.55, 'Task': 'MG - Generate'},#concrete
    {'User': 'P10(S)', 'Start': 23.09, 'End': 23.09, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P10(S)', 'Start': 23.36, 'End': 23.36, 'Task': 'Click Object'}, #umbrella frames 
    {'User': 'P10(S)', 'Start': 23.46, 'End': 23.46, 'Task': 'Click Object'}, #umbrella canopies
    {'User': 'P10(S)', 'Start': 24.06, 'End': 24.06, 'Task': 'Color Texture'}, # Soft Green 1
    #"can we get the material of the sidetable and apply it to the pool chair's base?"
    {'User': 'P10(S)', 'Start': 24.38, 'End': 24.38, 'Task': 'Click Object'}, #patio seat cushion
    {'User': 'P10(S)', 'Start': 24.44, 'End': 24.44, 'Task': 'Click Object'}, #patio frame
    {'User': 'P10(S)', 'Start': 24.52, 'End': 24.52, 'Task': 'Click Object'}, #sidetable
    {'User': 'P10(S)', 'Start': 27.28, 'End': 27.28, 'Task': 'Click Object'}, #fences
    {'User': 'P10(S)', 'Start': 27.54, 'End': 29.10, 'Task': 'Render'}, 
    #"Is it normal to have that checkerboard there?"
    {'User': 'P10(S)', 'Start': 30.22, 'End': 30.22, 'Task': 'Click Object'}, #patio chair cushion
    # {'User': 'P10(S)', 'Start': 36.46, 'End': 37.01, 'Task': 'Save'}, 
    {'User': 'P10(S)', 'Start': 31.46, 'End': 32.01, 'Task': 'Save'}, 
    

    {'User': 'P11(P)', 'Start': 0.13, 'End': 0.13, 'Task': 'Click Object'}, #floor
    {'User': 'P11(P)', 'Start': 0.33, 'End': 1.04, 'Task': 'MG - Generate'}, #tropical patio flooring
    #MG  set number 6
    # "Do these resemble tropical flooring?" "They do but they're a bit outdated."
    {'User': 'P11(P)', 'Start': 1.40, 'End': 2.13, 'Task': 'CB - Query Material'}, #tropical patio flooring
    {'User': 'P11(P)', 'Start': 3.14, 'End': 3.58, 'Task': 'CB-MG - Generate More'}, # generate more ceramic tiles with a natural stone look (CB)
    {'User': 'P11(P)', 'Start': 4.45, 'End': 5.31, 'Task': 'MG - Generate'}, #Similar textures ceramic tiles 4
    {'User': 'P11(P)', 'Start': 5.52, 'End': 5.52, 'Task': 'MG - Apply'}, #similar ceramic tiles 6
    # {'User': 'P11(P)', 'Start': 6.13, 'End': 6.13, 'Task': 'Scale Texture'}, #15
    {'User': 'P11(P)', 'Start': 7.40, 'End': 7.40, 'Task': 'Click Object'}, #pool edge
    {'User': 'P11(P)', 'Start': 7.57, 'End': 8.41, 'Task': 'MG - Generate'}, #pool tiles
    # {'User': 'P11(P)', 'Start': 9.12, 'End': 9.12, 'Task': 'MG - Add Keyword'}, #coastal
    {'User': 'P11(P)', 'Start': 9.29, 'End': 10.11, 'Task': 'MG - Generate'}, #pool tiles, coastal
    {'User': 'P11(P)', 'Start': 10.53, 'End': 10.53, 'Task': 'MG - Apply'}, #pool tiles 2
    # {'User': 'P11(P)', 'Start': 11.16, 'End': 11.16, 'Task': 'Scale Texture'}, #8.0
    {'User': 'P11(P)', 'Start': 12.36, 'End': 12.36, 'Task': 'MG - Brainstorm'}, # "weather-resistant", "woven pattern", "light brown"
    {'User': 'P11(P)', 'Start': 13.08, 'End': 13.54, 'Task': 'MG - Generate'}, #synthetic rattan
    {'User': 'P11(P)', 'Start': 14.35, 'End': 14.35, 'Task': 'Click Object'}, #sofa chair bases and coffee table base
    {'User': 'P11(P)', 'Start': 14.54, 'End': 14.54, 'Task': 'Click Object'}, #sofa chair bases and coffee table base
    {'User': 'P11(P)', 'Start': 15.12, 'End': 15.12, 'Task': 'MG - Apply'}, # synthetic rattan 5
    # {'User': 'P11(P)', 'Start': 15.21, 'End': 15.21, 'Task': 'Scale Texture'}, #8.0
    # {'User': 'P11(P)', 'Start': 15.46, 'End': 15.46, 'Task': 'Rotate Texture'}, #90
    {'User': 'P11(P)', 'Start': 16.24, 'End': 16.24, 'Task': 'Click Object'}, #sofa chair bases and coffee table base
    {'User': 'P11(P)', 'Start': 16.49, 'End': 16.49, 'Task': 'Color Texture'}, #brown
    {'User': 'P11(P)', 'Start': 18.43, 'End': 18.43, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P11(P)', 'Start': 19.17, 'End': 20.05, 'Task': 'MG - Generate'}, #terrazzo
    {'User': 'P11(P)', 'Start': 20.37, 'End': 20.37, 'Task': 'MG - Apply'}, #terrazzo 3
    {'User': 'P11(P)', 'Start': 21.11, 'End': 22.02, 'Task': 'MG - Generate'}, #outdoor fabric
    {'User': 'P11(P)', 'Start': 22.22, 'End': 22.22, 'Task': 'Click Object'}, #sofa chair cushions and pillows
    {'User': 'P11(P)', 'Start': 22.34, 'End': 22.34, 'Task': 'MG - Apply'}, #outdoor fabric 1
    # {'User': 'P11(P)', 'Start': 22.45, 'End': 22.45, 'Task': 'Scale Texture'}, #12
    {'User': 'P11(P)', 'Start': 23.42, 'End': 24.24, 'Task': 'CB - Query Material'}, #low maintenance wood fence material
    # "walang tumama. that is so interesting"
    {'User': 'P11(P)', 'Start': 25.15, 'End': 25.42, 'Task': 'CB - Query Material'}, #coastal wood
    {'User': 'P11(P)', 'Start': 26.20, 'End': 26.20, 'Task': 'Click Object'}, #fences
    {'User': 'P11(P)', 'Start': 26.28, 'End': 26.28, 'Task': 'CB - Apply'}, #teak wood
    {'User': 'P11(P)', 'Start': 26.40, 'End': 26.40, 'Task': 'Click Object'}, #fences
    {'User': 'P11(P)', 'Start': 27.05, 'End': 27.05, 'Task': 'Click Object'}, #sofa chair frames and coffee table base
    # {'User': 'P11(P)', 'Start': 27.28, 'End': 27.28, 'Task': 'Set Normal'}, #5
    # {'User': 'P11(P)', 'Start': , 'End': , 'Task': 'Color Texture'}, #Soft Green 3
    {'User': 'P11(P)', 'Start': 28.06, 'End': 28.06, 'Task': 'Click Object'}, #coffee table top
    # {'User': 'P11(P)', 'Start': 28.10, 'End': 28.10, 'Task': 'Set Roughness'}, #0.2
    {'User': 'P11(P)', 'Start': 29.47, 'End': 30.18, 'Task': 'Render'},
    # """can you render from that point of view?"" ""No, you the rendering is from a fixed point."""
    # "it's not reflected on the flooring"
    {'User': 'P11(P)', 'Start': 31.12, 'End': 31.43, 'Task': 'Save'}, 
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Assign a color to each unique task
color_map = {
    'Click Object': 'gray',

    'MG - Generate': 'green',
    'MG - Apply': 'green',
    'MG - Add Keyword': 'lightgreen',
    'MG - Brainstorm': 'lime',

    'CB - Query Material': 'blue',
    'CB - Query Color': 'lightblue',
    'CB - Apply': 'blue',
    'CB - Save Color': 'pink',

    'CB-MG - Generate More':'cyan',

    # 'Scale Texture': 'magenta',
    # 'Rotate Texture': 'indigo',
    # 'Translate Texture': 'pink',
    'Color Texture': 'purple',

    # 'Set Metalness': 'black',
    # 'Set Roughness': 'brown',
    # 'Set Opacity': 'red',
    
    
    'Render': 'yellow',
    'Save': 'black',

    # 'Set Normal': 'black',
}

df['Color'] = df['Task'].map(color_map)

# Tasks to be represented as points instead of bars
point_tasks = ['Click Object', 'MG - Apply', 'CB - Apply', 'Set Metalness', 'Set Roughness', 'Set Opacity', 'Color Texture', 'Scale Texture', 'Rotate Texture',  'MG - Add Keyword', 'CB - Save Color', 'MG - Brainstorm','Translate Texture', 'Save', 'Set Normal']

# Plot
fig, ax = plt.subplots(figsize=(23, 13))


for i, row in df.iterrows():

    if row['Task'] == 'MG - Generate':
        if row['User'] not in mg_durations.keys():
            mg_durations[row['User']] = []
        mg_durations[row['User']].append(convert_to_seconds(row['End']) - convert_to_seconds(row['Start']))
    if row['Task'] == 'CB - Query Material':
        if row['User'] not in cb_durations.keys():
            cb_durations[row['User']] = []
        cb_durations[row['User']].append(convert_to_seconds(row['End']) - convert_to_seconds(row['Start']))
    if row['Task'] == 'CB - Query Color':
        if row['User'] not in cb_durations.keys():
            cb_durations[row['User']] = []
        cb_durations[row['User']].append(convert_to_seconds(row['End']) - convert_to_seconds(row['Start']))
    if row['Task'] == 'MG-CB - Generate More':
        if row['User'] not in mg_durations.keys():
            mg_durations[row['User']] = []
        mg_durations[row['User']].append(convert_to_seconds(row['End']) - convert_to_seconds(row['Start']))
    

    # Get the index of the participant to determine vertical position (y-axis)
    participant_idx = df['User'].unique().tolist().index(row['User'])

    if row['Task'] in point_tasks:
    #     # Use scatter for tasks that are represented as points
    #     if row['Task'] == 'Click Object':
    #         add_icon(ax, icons_dict['Click Object'], row['Start'], participant_idx, zoom=0.04)
    #         pass
    #     else:
    #         ax.scatter(row['Start'], row['User'], color=row['Color'], s=60, marker='o', label=row['Task'])
        ax.scatter(row['Start'], row['User'], color=row['Color'], s=100, marker='o', label=row['Task'])
    else:
        # Use barh for tasks that are represented as bars
        ax.barh(row['User'], row['End'] - row['Start'], left=row['Start'], height=0.4, color=row['Color'], label=row['Task'])


# Set a tighter x-axis range to minimize the dead space on the left and right
ax.set_xlim(left=0, right=df['End'].max() + 1)

# # Custom legend icons
# custom_legend_elements = [
#     plt.Line2D([0], [0], marker='o', color='w', label='Click Object', markerfacecolor='gray', markersize=10),
#     plt.Line2D([0], [0], marker='o', color='w', label='MG - Generate', markerfacecolor='green', markersize=10),
#     plt.Line2D([0], [0], marker='o', color='w', label='CB - Query Material', markerfacecolor='blue', markersize=10),
# ]
# # Add the icon to the legend as an image
# icon = get_icon_image(icons_dict['Click Object'], zoom=0.04)
# custom_legend_elements.append(OffsetImage(icon, zoom=0.05))
# ax.legend(handles=custom_legend_elements, loc='upper left', bbox_to_anchor=(0.90, 1), title="Actions", fontsize=7)

font_size=18
# Create a legend with unique tasks
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys(), title="Actions", loc='upper left', bbox_to_anchor=(0.80, 1), fontsize=font_size, markerscale=1.2, handletextpad=0.5)

ax.tick_params(axis='both', labelsize=font_size)  # Increase font size of x & y axis values

# Format x-axis to show minutes
plt.xlabel('Minutes', fontsize=font_size)
plt.ylabel('User', fontsize=font_size)
# plt.title('User Activity Timeline')

for key in mg_durations.keys():
    print(f'{np.mean(mg_durations[key])}')
    # print(f'Sum {key} MG: {sum(mg_durations[key])}')
print("====================================")
for key in cb_durations.keys():
    print(f'{np.mean(cb_durations[key])}')
    # print(f'Sum {key} CB: {sum(cb_durations[key])}')

plt.grid(True)
# Adjust layout to ensure the legend is not cut off
plt.tight_layout(rect=[0, 0, 1, 1])
plt.show()
pass