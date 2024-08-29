import matplotlib.pyplot as plt
import pandas as pd

# List of dictionaries representing each user action
data = [
    {'User': 'P1', 'Start': 0.13, 'End': 0.13, 'Task': 'Click Object'},
    {'User': 'P1', 'Start': 0.20, 'End': 0.55, 'Task': 'MG - Generate'}, #wood deck
    # {'User': 'P1', 'Start': 0.26, 'End': 0.32, 'Task': 'Read Brief'},
    {'User': 'P1', 'Start': 0.57, 'End': 0.57, 'Task': 'MG - Apply'}, #wood deck 2
    {'User': 'P1', 'Start': 0.57, 'End': 0.57, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 1.10, 'End': 1.10, 'Task': 'MG - Apply'}, #wood deck 1
    {'User': 'P1', 'Start': 1.11, 'End': 1.11, 'Task': 'MG - Apply'}, #wood deck 2
    {'User': 'P1', 'Start': 1.19, 'End': 1.30, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 1.40, 'End': 1.40, 'Task': 'MG - Apply'}, #wood deck 1
    {'User': 'P1', 'Start': 1.43, 'End': 1.45, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 2.08, 'End': 2.42, 'Task': 'MG - Generate'}, #gray nonskid tiles
    {'User': 'P1', 'Start': 2.52, 'End': 2.52, 'Task': 'MG - Apply'}, #gray nonskid tiles 2
    {'User': 'P1', 'Start': 2.55, 'End': 2.57, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 3.04, 'End': 4.11, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 4.21, 'End': 4.21, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 4.27, 'End': 4.27, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1', 'Start': 4.34, 'End': 5.07, 'Task': 'MG - Generate'}, #pool tiles 
    {'User': 'P1', 'Start': 5.13, 'End': 5.13, 'Task': 'MG - Apply'}, #pool tiles 2
    {'User': 'P1', 'Start': 5.17, 'End': 5.17, 'Task': 'MG - Apply'}, #pool tiles 4
    {'User': 'P1', 'Start': 5.43, 'End': 5.54, 'Task': 'Color Texture'}, #pool tiles
    {'User': 'P1', 'Start': 5.55, 'End': 5.55, 'Task': 'Click Object'}, #lounge chair seat
    {'User': 'P1', 'Start': 6.20, 'End': 7.21, 'Task': 'CB - Query Material'}, #Can you suggest cloth material for the pool beds?
    {'User': 'P1', 'Start': 6.45, 'End': 6.45, 'Task': 'Click Object'}, #left fence
    {'User': 'P1', 'Start': 7.10, 'End': 8.21, 'Task': 'MG - Generate'}, #wood slats
    {'User': 'P1', 'Start': 7.29, 'End': 7.29, 'Task': 'Click Object'}, #umbrella canopy
    {'User': 'P1', 'Start': 7.30, 'End': 7.30, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 1
    {'User': 'P1', 'Start': 7.44, 'End': 7.48, 'Task': 'Color Texture'}, #umbrella canopy 1
    {'User': 'P1', 'Start': 8.08, 'End': 8.08, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 2
    {'User': 'P1', 'Start': 8.14, 'End': 8.19, 'Task': 'Color Texture'}, #umbrella canopy 2
    {'User': 'P1', 'Start': 8.23, 'End': 8.23, 'Task': 'Click Object'}, #left fence
    {'User': 'P1', 'Start': 8.25, 'End': 8.25, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1', 'Start': 8.33, 'End': 8.33, 'Task': 'Click Object'}, #right fence
    {'User': 'P1', 'Start': 8.36, 'End': 8.36, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1', 'Start': 8.41, 'End': 8.41, 'Task': 'Click Object'}, #right fence
    {'User': 'P1', 'Start': 8.49, 'End': 9.00, 'Task': 'Scale Texture'}, #right fence
    {'User': 'P1', 'Start': 9.11, 'End': 10.34, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 10.57, 'End': 10.57, 'Task': 'Click Object'}, #umbrella canopy 2
    {'User': 'P1', 'Start': 10.59, 'End': 10.59, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1', 'Start': 11.54, 'End': 12.28, 'Task': 'MG - Generate'}, #gray cloth
    {'User': 'P1', 'Start': 12.41, 'End': 13.15, 'Task': 'MG - Generate'}, #cloth
    {'User': 'P1', 'Start': 13.30, 'End': 13.37, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P1', 'Start': 13.39, 'End': 13.39, 'Task': 'MG - Apply'}, #cloth
    {'User': 'P1', 'Start': 15.30, 'End': 15.41, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P1', 'Start': 15.45, 'End': 15.47, 'Task': 'Scale Texture'}, #lounge chair cushions
    {'User': 'P1', 'Start': 16.08, 'End': 16.45, 'Task': 'MG - Generate'}, #powdercoated
    {'User': 'P1', 'Start': 17.02, 'End': 17.42, 'Task': 'Click Object'}, #umbrella poles and lounge chair frames
    {'User': 'P1', 'Start': 17.43, 'End': 17.46, 'Task': 'Color Texture'}, #umbrella poles and lounge chair frames
    {'User': 'P1', 'Start': 17.48, 'End': 17.49, 'Task': 'Set Metalness'}, # 1
    {'User': 'P1', 'Start': 17.50, 'End': 17.51, 'Task': 'Set Roughness'}, # 0
    {'User': 'P1', 'Start': 18.19, 'End': 18.53, 'Task': 'MG - Generate'}, #weaved
    {'User': 'P1', 'Start': 19.03, 'End': 20.36, 'Task': 'MG - Generate'}, #weaved rattan, setted number to 10
    {'User': 'P1', 'Start': 19.37, 'End': 20.59, 'Task': 'Render'},  
    {'User': 'P1', 'Start': 21.08, 'End': 21.08, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P1', 'Start': 21.10, 'End': 21.10, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1', 'Start': 21.18, 'End': 21.27, 'Task': 'Click Object'}, #sofa chair frames, coffee table base
    {'User': 'P1', 'Start': 21.30, 'End': 21.30, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1', 'Start': 21.31, 'End': 21.31, 'Task': 'MG - Apply'}, #weaved rattan 3
    {'User': 'P1', 'Start': 21.35, 'End': 21.38, 'Task': 'Scale Texture'}, #sofa chair frames, coffee table base
    {'User': 'P1', 'Start': 21.43, 'End': 21.51, 'Task': 'Color Texture'}, #sofa chair frames, coffee table base, yellow
    {'User': 'P1', 'Start': 22.03, 'End': 23.39, 'Task': 'MG - Generate'}, #cotton material
    {'User': 'P1', 'Start': 22.19, 'End': 22.19, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 23.30, 'End': 25.04, 'Task': 'CB - Query Material'}, #Can you suggest similar materials to gray nonskid tiles for a floor?
    {'User': 'P1', 'Start': 23.42, 'End': 24.05, 'Task': 'Click Object'}, #sofa cushions and pillows
    {'User': 'P1', 'Start': 24.09, 'End': 24.09, 'Task': 'MG - Apply'}, #cotton material 4
    {'User': 'P1', 'Start': 24.20, 'End': 24.26, 'Task': 'Click Object'}, #sofa cushions and pillows 
    {'User': 'P1', 'Start': 24.28, 'End': 24.28, 'Task': 'MG - Apply'}, #cotton material 7
    {'User': 'P1', 'Start': 24.40, 'End': 24.43, 'Task': 'Scale Texture'}, #sofa cushions and pillows 
    {'User': 'P1', 'Start': 24.48, 'End': 24.48, 'Task': 'Click Object'}, #coffee table
    {'User': 'P1', 'Start': 24.58, 'End': 25.51, 'Task': 'MG - Generate'}, #glass
    {'User': 'P1', 'Start': 25.04, 'End': 25.04, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 25.10, 'End': 25.10, 'Task': 'CB - Apply'}, #rubber flooring
    {'User': 'P1', 'Start': 25.11, 'End': 25.13, 'Task': 'Scale Texture'}, #floor
    {'User': 'P1', 'Start': 26.02, 'End': 26.02, 'Task': 'Click Object'}, #coffee table top
    {'User': 'P1', 'Start': 26.10, 'End': 26.10, 'Task': 'MG - Apply'}, #glass 3
    {'User': 'P1', 'Start': 26.58, 'End': 28.10, 'Task': 'Render'}, #glass 4
    {'User': 'P1', 'Start': 28.25, 'End': 29.30, 'Task': 'MG - Generate'}, #Rubber Flooring, from CB
    {'User': 'P1', 'Start': 28.30, 'End': 28.30, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 28.46, 'End': 28.46, 'Task': 'Click Object'}, #right fence
    {'User': 'P1', 'Start': 28.51, 'End': 28.51, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1', 'Start': 29.27, 'End': 29.27, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 29.28, 'End': 29.28, 'Task': 'MG - Apply'}, #rubber floor 2
    {'User': 'P1', 'Start': 29.29, 'End': 29.29, 'Task': 'MG - Apply'}, #rubber floor 4
    {'User': 'P1', 'Start': 29.30, 'End': 29.30, 'Task': 'MG - Apply'}, #rubber floor 6
    {'User': 'P1', 'Start': 29.31, 'End': 29.31, 'Task': 'MG - Apply'}, #rubber floor 5
    {'User': 'P1', 'Start': 29.32, 'End': 29.32, 'Task': 'MG - Apply'}, #rubber floor 3
    {'User': 'P1', 'Start': 29.54, 'End': 29.44, 'Task': 'MG - Generate'}, #Stone flooring
    {'User': 'P1', 'Start': 30.32, 'End': 30.50, 'Task': 'Save'},
    {'User': 'P1', 'Start': 30.52, 'End': 30.52, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 30.55, 'End': 30.55, 'Task': 'MG - Apply'}, #stone flooring 6
    {'User': 'P1', 'Start': 31.00, 'End': 31.02, 'Task': 'Scale Texture'}, #stone flooring 4
    {'User': 'P1', 'Start': 31.03, 'End': 32.26, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 32.30, 'End': 32.47, 'Task': 'Save'},

    {'User': 'P3', 'Start': 0.10, 'End': 0.10, 'Task': 'Click Object'}, #pool edge
    {'User': 'P3', 'Start': 0.30, 'End': 1.06, 'Task': 'MG - Generate'}, #blue tiles
    {'User': 'P3', 'Start': 1.20, 'End': 1.20, 'Task': 'MG - Apply'}, #blue tiles 2
    {'User': 'P3', 'Start': 1.43, 'End': 1.47, 'Task': 'Set Roughness'}, #0.1
    {'User': 'P3', 'Start': 1.53, 'End': 1.55, 'Task': 'Set Roughness'}, #0.2
    {'User': 'P3', 'Start': 2.08, 'End': 2.08, 'Task': 'Click Object'}, #floor
    {'User': 'P3', 'Start': 2.21, 'End': 2.55, 'Task': 'MG - Generate'}, #wood deck
    {'User': 'P3', 'Start': 3.05, 'End': 3.05, 'Task': 'MG - Apply'}, #wood deck 3
    {'User': 'P3', 'Start': 3.10, 'End': 3.10, 'Task': 'Click Object'}, #floor
    {'User': 'P3', 'Start': 3.14, 'End': 3.33, 'Task': 'Scale Texture'}, #40
    {'User': 'P3', 'Start': 3.48, 'End': 3.48, 'Task': 'Click Object'}, #2 lounge chair cushions
    {'User': 'P3', 'Start': 3.55, 'End': 4.31, 'Task': 'MG - Generate'}, #rattan
    {'User': 'P3', 'Start': 3.59, 'End': 4.01, 'Task': 'Click Object'}, #2 lounge chair cushions
    {'User': 'P3', 'Start': 4.45, 'End': 4.45, 'Task': 'MG - Apply'}, #rattan 1
    {'User': 'P3', 'Start': 4.49, 'End': 4.55, 'Task': 'Scale Texture'}, #10
    {'User': 'P3', 'Start': 5.03, 'End': 5.03, 'Task': 'Click Object'}, #1 lounge chair frame
    {'User': 'P3', 'Start': 5.10, 'End': 5.14, 'Task': 'Color Texture'}, #white (didn't work)
    {'User': 'P3', 'Start': 5.15, 'End': 5.15, 'Task': 'Click Object'}, #1 lounge chair frame
    {'User': 'P3', 'Start': 5.18, 'End': 5.23, 'Task': 'Color Texture'}, #white (didn't work)
    {'User': 'P3', 'Start': 5.28, 'End': 5.28, 'Task': 'Click Object'}, #2 lounge chair frames
    {'User': 'P3', 'Start': 5.49, 'End': 6.25, 'Task': 'MG - Generate'}, #metal, white
    {'User': 'P3', 'Start': 6.33, 'End': 6.41, 'Task': 'MG - Brainstorm Keywords'}, #shiny, reflective
    {'User': 'P3', 'Start': 6.55, 'End': 7.31, 'Task': 'MG - Generate'}, #metal, white, shiny, reflective
    {'User': 'P3', 'Start': 7.38, 'End': 7.38, 'Task': 'MG - Apply'}, #metal, white, shiny, reflective 4
    {'User': 'P3', 'Start': 7.44, 'End': 7.46, 'Task': 'Click Object'}, #2 lounge chair frames
    {'User': 'P3', 'Start': 8.02, 'End': 8.02, 'Task': 'Click Object'}, #1 umbrella canopy
    {'User': 'P3', 'Start': 8.32, 'End': 8.54, 'Task': 'MG - Generate'}, #green fabric
    {'User': 'P3', 'Start': 9.05, 'End': 9.05, 'Task': 'MG - Apply'}, #green fabric 1
    {'User': 'P3', 'Start': 9.15, 'End': 9.19, 'Task': 'Scale Texture'}, #5
    {'User': 'P3', 'Start': 9.32, 'End': 9.32, 'Task': 'Click Object'}, #1 umbrella frame
    {'User': 'P3', 'Start': 9.49, 'End': 9.53, 'Task': 'MG - Brainstorm Keywords'}, #shiny, reflective, smooth 
    {'User': 'P3', 'Start': 10.05, 'End': 10.41, 'Task': 'MG - Generate'}, #metal, shiny, reflective, smooth
    {'User': 'P3', 'Start': 10.50, 'End': 10.50, 'Task': 'MG - Apply'}, #metal, shiny, reflective, smooth 2
    {'User': 'P3', 'Start': 11.0, 'End': 11.0, 'Task': 'Click Object'}, #1 sidetable
    {'User': 'P3', 'Start': 11.14, 'End': 11.49, 'Task': 'MG - Generate'}, #wood, white
    {'User': 'P3', 'Start': 12.01, 'End': 12.06, 'Task': 'MG - Brainstorm Keywords'}, #shiny, reflective, smooth 
    {'User': 'P3', 'Start': 12.23, 'End': 12.23, 'Task': 'MG - Apply'}, #wood 2
    {'User': 'P3', 'Start': 12.32, 'End': 12.41, 'Task': 'Set Roughness'}, #0.1
    {'User': 'P3', 'Start': 12.49, 'End': 12.55, 'Task': 'Rotate Texture'}, #90
    {'User': 'P3', 'Start': 13.19, 'End': 13.25, 'Task': 'Click Object'}, #Sofa cushions
    {'User': 'P3', 'Start': 13.35, 'End': 14.11, 'Task': 'MG - Generate'}, #Light blue fabric
    {'User': 'P3', 'Start': 14.18, 'End': 14.18, 'Task': 'MG - Apply'}, #Light blue fabric 1
    {'User': 'P3', 'Start': 14.31, 'End': 14.35, 'Task': 'Click Object'}, #Sofa frames and coffee table base  
    {'User': 'P3', 'Start': 14.41, 'End': 15.15, 'Task': 'MG - Generate'}, #white rattan
    {'User': 'P3', 'Start': 15.21, 'End': 15.21, 'Task': 'MG - Apply'}, #white rattan 1
    {'User': 'P3', 'Start': 15.25, 'End': 15.25, 'Task': 'MG - Apply'}, #white rattan 2
    {'User': 'P3', 'Start': 15.33, 'End': 15.36, 'Task': 'Color Texture'},   
    {'User': 'P3', 'Start': 15.43, 'End': 15.47, 'Task': 'Scale Texture'}, #10
    {'User': 'P3', 'Start': 15.53, 'End': 15.53, 'Task': 'Click Object'}, #Floor
    {'User': 'P3', 'Start': 15.57, 'End': 16.02, 'Task': 'Click Object'}, #Sofa frames and coffee table base  
    {'User': 'P3', 'Start': 16.04, 'End': 16.04, 'Task': 'Click Object'}, #Coffee table top
    {'User': 'P3', 'Start': 16.13, 'End': 16.49, 'Task': 'MG - Generate'}, #clear glass
    {'User': 'P3', 'Start': 16.55, 'End': 16.59, 'Task': 'MG - Brainstorm Keywords'}, #smooth, reflective
    {'User': 'P3', 'Start': 17.11, 'End': 17.45, 'Task': 'MG - Generate'}, #clear glass, smooth, relective
    {'User': 'P3', 'Start': 17.53, 'End': 17.53, 'Task': 'MG - Apply'}, #clear glass, smooth, relective 2
    {'User': 'P3', 'Start': 17.55, 'End': 17.55, 'Task': 'Click Object'}, #Coffee table top
    {'User': 'P3', 'Start': 18.01, 'End': 18.04, 'Task': 'Click Object'}, #Sofa pillows
    {'User': 'P3', 'Start': 18.14, 'End': 18.51, 'Task': 'MG - Generate'}, #light grey fabric
    {'User': 'P3', 'Start': 18.56, 'End': 18.56, 'Task': 'MG - Apply'},  #light grey fabric 2
    {'User': 'P3', 'Start': 19.03, 'End': 19.03, 'Task': 'Click Object'}, #Fences
    {'User': 'P3', 'Start': 19.18, 'End': 19.53, 'Task': 'MG - Generate'}, #oak wood
    {'User': 'P3', 'Start': 20.06, 'End': 20.06, 'Task': 'MG - Apply'},  #oak wood 4
    {'User': 'P3', 'Start': 20.26, 'End': 20.25, 'Task': 'Color Texture'}, 
    {'User': 'P3', 'Start': 20.29, 'End': 20.31, 'Task': 'Click Object'}, #Fences
    {'User': 'P3', 'Start': 20.57, 'End': 21.01, 'Task': 'Click Object'}, #Other 2 patio chair cushions
    {'User': 'P3', 'Start': 21.16, 'End': 21.50, 'Task': 'MG - Generate'}, #rattan
    {'User': 'P3', 'Start': 22.07, 'End': 22.07, 'Task': 'MG - Apply'},  #rattan 3
    {'User': 'P3', 'Start': 22.15, 'End': 22.18, 'Task': 'Color Texture'}, 
    {'User': 'P3', 'Start': 22.19, 'End': 22.21, 'Task': 'Click Object'}, #Other 2 patio chair cushions
    {'User': 'P3', 'Start': 22.23, 'End': 22.30, 'Task': 'Scale Texture'}, 
    {'User': 'P3', 'Start': 22.34, 'End': 22.41, 'Task': 'Click Object'}, # umbrella metals, patio chair frames, dining table, and dining chairs
    {'User': 'P3', 'Start': 23.13, 'End': 23.48, 'Task': 'MG - Generate'}, #white metal
    {'User': 'P3', 'Start': 23.56, 'End': 23.58, 'Task': 'MG - Brainstorm Keywords'}, #shiny, reflective, smooth
    {'User': 'P3', 'Start': 24.06, 'End': 24.42, 'Task': 'MG - Generate'}, #white metal, shiny, reflective, smooth
    {'User': 'P3', 'Start': 24.49, 'End': 24.49, 'Task': 'MG - Apply'}, #white metal, shiny, reflective, smooth 1
    {'User': 'P3', 'Start': 25.03, 'End': 25.03, 'Task': 'Click Object'}, #Other umbrella canopy
    {'User': 'P3', 'Start': 25.10, 'End': 25.46, 'Task': 'MG - Generate'}, #white metal, shiny, reflective, smooth
    {'User': 'P3', 'Start': 25.52, 'End': 25.52, 'Task': 'MG - Apply'}, #green fabric 1
    {'User': 'P3', 'Start': 26.03, 'End': 26.03, 'Task': 'Click Object'}, #Other sidetable
    {'User': 'P3', 'Start': 26.13, 'End': 26.50, 'Task': 'MG - Generate'}, #wood
    {'User': 'P3', 'Start': 26.55, 'End': 27.33, 'Task': 'MG - Generate'}, #wood, white
    {'User': 'P3', 'Start': 27.51, 'End': 27.53, 'Task': 'Rotate Texture'}, #90
    {'User': 'P3', 'Start': 28.15, 'End': 29.42, 'Task': 'Render'}, 
    {'User': 'P3', 'Start': 30.45, 'End': 30.54, 'Task': 'Save'}, 

    {'User': 'P4', 'Start': 0.41, 'End': 0.50, 'Task': 'CB - Query Color'}, #Suggest color palettes that involve monochromatic blues.
    {'User': 'P4', 'Start': 1.00, 'End': 1.00, 'Task': 'CB - Save Color'}, #Cool and Serene
    {'User': 'P4', 'Start': 1.08, 'End': 1.10, 'Task': 'Click Object'}, #Fences
    {'User': 'P4', 'Start': 1.38, 'End': 2.13, 'Task': 'MG - Generate'}, #white wood
    {'User': 'P4', 'Start': 2.29, 'End': 2.29, 'Task': 'MG - Apply'}, #white wood 4
    {'User': 'P4', 'Start': 3.37, 'End': 3.42, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P4', 'Start': 4.10, 'End': 4.47, 'Task': 'MG - Generate'}, #leather
    {'User': 'P4', 'Start': 5.18, 'End': 5.18, 'Task': 'MG - Add Keyword'}, #matte
    {'User': 'P4', 'Start': 5.25, 'End': 7.00, 'Task': 'MG - Generate'}, #leather, matte
    {'User': 'P4', 'Start': 7.20, 'End': 7.20, 'Task': 'MG - Apply'}, #leather, matte 3
    {'User': 'P4', 'Start': 7.27, 'End': 7.48, 'Task': 'Scale Texture'}, #leather, matte 4
    {'User': 'P4', 'Start': 8.18, 'End': 8.18, 'Task': 'Color Texture'}, #Cool and Serene 1

    # {'User': 'P4', 'Start': 39.05, 'End': 39.30, 'Task': 'CB - Query Material'},
    # {'User': 'P4', 'Start': 39.30, 'End': 39.57, 'Task': 'MG - Generate'},
    # {'User': 'P4', 'Start': 39.57, 'End': 40.00, 'Task': 'MG - Apply'},
    # {'User': 'P5', 'Start': 28.24, 'End': 28.45, 'Task': 'Click Object'},
    # {'User': 'P6', 'Start': 42.07, 'End': 42.20, 'Task': 'CB - Query Material'},
    # {'User': 'P6', 'Start': 42.57, 'End': 43.07, 'Task': 'MG - Apply'},
    # {'User': 'P7', 'Start': 42.00, 'End': 42.20, 'Task': 'Click Object'},
    # {'User': 'P8', 'Start': 1.20, 'End': 1.40, 'Task': 'Click Object'},
    # {'User': 'P9', 'Start': 45.35, 'End': 45.57, 'Task': 'CB - Query Material'},
    # {'User': 'P10', 'Start': 5.00, 'End': 5.20, 'Task': 'Click Object'},
    # {'User': 'P11', 'Start': 5.40, 'End': 6.00, 'Task': 'CB - Query Material'},
    # {'User': 'P12', 'Start': 48.32, 'End': 49.00, 'Task': 'Click Object'},
]

# Convert to DataFrame
df = pd.DataFrame(data)

# Assign a color to each unique task
color_map = {
    'Click Object': 'gray',
    'MG - Generate': 'green',
    'Read Brief': 'red',
    'MG - Apply': 'cyan',
    'Scale Texture': 'magenta',
    'Rotate Texture': 'indigo',
    'Render': 'yellow',
    'Color Texture': 'purple',
    'CB - Query Material': 'orange',
    'CB - Apply': 'blue',
    'Set Metalness': 'black',
    'Set Roughness': 'brown',
    'Save': 'pink',
    'MG - Brainstorm Keywords': 'lime'

}

df['Color'] = df['Task'].map(color_map)

# Tasks to be represented as points instead of bars
point_tasks = ['Click Object', 'MG - Apply']

# Plot
fig, ax = plt.subplots(figsize=(12, 6))

for i, row in df.iterrows():
    if row['Task'] in point_tasks and row['End'] == row['Start']:
        # Use scatter for tasks that are represented as points
        ax.scatter(row['Start'], row['User'], color=row['Color'], s=100, marker='o', label=row['Task'])
    else:
        # Use barh for tasks that are represented as bars
        ax.barh(row['User'], row['End'] - row['Start'], left=row['Start'], height=0.4, color=row['Color'], label=row['Task'])

# Create a legend with unique tasks
handles, labels = ax.get_legend_handles_labels()
unique_labels = dict(zip(labels, handles))
ax.legend(unique_labels.values(), unique_labels.keys(), title="Tasks", loc='upper right')

# Format x-axis to show minutes
plt.xlabel('Minutes')
plt.ylabel('User')
plt.title('User Activity Timeline (Minutes) with Tasks as Points and Bars')

plt.grid(True)
plt.show()
pass