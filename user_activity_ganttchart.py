import matplotlib.pyplot as plt
import pandas as pd

# List of dictionaries representing each user action
data = [
    {'User': 'P1', 'Start': 5.13, 'End': 5.13, 'Task': 'Click Object'},
    {'User': 'P1', 'Start': 5.20, 'End': 5.55, 'Task': 'MG - Generate'}, #wood deck
    # {'User': 'P1', 'Start': 5.26, 'End': 5.32, 'Task': 'Read Brief'},
    {'User': 'P1', 'Start': 5.57, 'End': 5.57, 'Task': 'MG - Apply'}, #wood deck 2
    {'User': 'P1', 'Start': 5.57, 'End': 5.57, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 6.10, 'End': 6.10, 'Task': 'MG - Apply'}, #wood deck 1
    {'User': 'P1', 'Start': 6.11, 'End': 6.11, 'Task': 'MG - Apply'}, #wood deck 2
    {'User': 'P1', 'Start': 6.19, 'End': 6.30, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 6.40, 'End': 6.40, 'Task': 'MG - Apply'}, #wood deck 1
    {'User': 'P1', 'Start': 6.43, 'End': 6.45, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 7.08, 'End': 7.42, 'Task': 'MG - Generate'}, #gray nonskid tiles
    {'User': 'P1', 'Start': 7.52, 'End': 7.52, 'Task': 'MG - Apply'}, #gray nonskid tiles 2
    {'User': 'P1', 'Start': 7.55, 'End': 7.57, 'Task': 'Scale Texture'}, #floor  
    {'User': 'P1', 'Start': 8.04, 'End': 9.11, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 9.21, 'End': 9.21, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 9.27, 'End': 9.27, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1', 'Start': 9.34, 'End': 10.07, 'Task': 'MG - Generate'}, #pool tiles 
    {'User': 'P1', 'Start': 10.13, 'End': 10.13, 'Task': 'MG - Apply'}, #pool tiles 2
    {'User': 'P1', 'Start': 10.17, 'End': 10.17, 'Task': 'MG - Apply'}, #pool tiles 4
    {'User': 'P1', 'Start': 10.43, 'End': 10.54, 'Task': 'Color Texture'}, #pool tiles
    {'User': 'P1', 'Start': 10.55, 'End': 10.55, 'Task': 'Click Object'}, #lounge chair seat
    {'User': 'P1', 'Start': 11.20, 'End': 12.21, 'Task': 'CB - Query Material'}, #Can you suggest cloth material for the pool beds?
    {'User': 'P1', 'Start': 11.45, 'End': 11.45, 'Task': 'Click Object'}, #left fence
    {'User': 'P1', 'Start': 12.10, 'End': 13.21, 'Task': 'MG - Generate'}, #wood slats
    {'User': 'P1', 'Start': 12.29, 'End': 12.29, 'Task': 'Click Object'}, #umbrella canopy
    {'User': 'P1', 'Start': 12.30, 'End': 12.30, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 1
    {'User': 'P1', 'Start': 12.44, 'End': 12.48, 'Task': 'Color Texture'}, #umbrella canopy 1
    {'User': 'P1', 'Start': 13.08, 'End': 13.08, 'Task': 'CB - Apply'}, #sunbrella fabric to canopy 2
    {'User': 'P1', 'Start': 13.14, 'End': 13.19, 'Task': 'Color Texture'}, #umbrella canopy 2
    {'User': 'P1', 'Start': 13.23, 'End': 13.23, 'Task': 'Click Object'}, #left fence
    {'User': 'P1', 'Start': 13.25, 'End': 13.25, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1', 'Start': 13.33, 'End': 13.33, 'Task': 'Click Object'}, #right fence
    {'User': 'P1', 'Start': 13.36, 'End': 13.36, 'Task': 'MG - Apply'}, #wood slats 4
    {'User': 'P1', 'Start': 13.41, 'End': 13.41, 'Task': 'Click Object'}, #right fence
    {'User': 'P1', 'Start': 13.49, 'End': 14.00, 'Task': 'Scale Texture'}, #right fence
    {'User': 'P1', 'Start': 14.11, 'End': 15.34, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 15.57, 'End': 15.57, 'Task': 'Click Object'}, #umbrella canopy 2
    {'User': 'P1', 'Start': 15.59, 'End': 15.59, 'Task': 'Click Object'}, #pool edge
    {'User': 'P1', 'Start': 16.54, 'End': 17.28, 'Task': 'MG - Generate'}, #gray cloth
    {'User': 'P1', 'Start': 17.41, 'End': 18.15, 'Task': 'MG - Generate'}, #cloth
    {'User': 'P1', 'Start': 18.30, 'End': 18.37, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P1', 'Start': 18.39, 'End': 18.39, 'Task': 'MG - Apply'}, #cloth
    {'User': 'P1', 'Start': 20.30, 'End': 20.41, 'Task': 'Click Object'}, #lounge chair cushions
    {'User': 'P1', 'Start': 20.45, 'End': 20.47, 'Task': 'Scale Texture'}, #lounge chair cushions
    {'User': 'P1', 'Start': 21.08, 'End': 21.45, 'Task': 'MG - Generate'}, #powdercoated
    {'User': 'P1', 'Start': 22.02, 'End': 22.42, 'Task': 'Click Object'}, #umbrella poles and lounge chair frames
    {'User': 'P1', 'Start': 22.43, 'End': 22.46, 'Task': 'Color Texture'}, #umbrella poles and lounge chair frames
    {'User': 'P1', 'Start': 22.48, 'End': 22.49, 'Task': 'Set Metalness'}, # 1
    {'User': 'P1', 'Start': 22.50, 'End': 22.51, 'Task': 'Set Roughness'}, # 0
    {'User': 'P1', 'Start': 23.19, 'End': 23.53, 'Task': 'MG - Generate'}, #weaved
    {'User': 'P1', 'Start': 24.03, 'End': 25.36, 'Task': 'MG - Generate'}, #weaved rattan, setted number to 10
    {'User': 'P1', 'Start': 24.37, 'End': 25.59, 'Task': 'Render'},  
    {'User': 'P1', 'Start': 26.08, 'End': 26.08, 'Task': 'Click Object'}, #sofa chair frame
    {'User': 'P1', 'Start': 26.10, 'End': 26.10, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1', 'Start': 26.18, 'End': 26.27, 'Task': 'Click Object'}, #sofa chair frames, coffee table base
    {'User': 'P1', 'Start': 26.30, 'End': 26.30, 'Task': 'MG - Apply'}, #weaved rattan 1
    {'User': 'P1', 'Start': 26.31, 'End': 26.31, 'Task': 'MG - Apply'}, #weaved rattan 3
    {'User': 'P1', 'Start': 26.35, 'End': 26.38, 'Task': 'Scale Texture'}, #sofa chair frames, coffee table base
    {'User': 'P1', 'Start': 26.43, 'End': 26.51, 'Task': 'Color Texture'}, #sofa chair frames, coffee table base, yellow
    {'User': 'P1', 'Start': 27.03, 'End': 28.39, 'Task': 'MG - Generate'}, #cotton material
    {'User': 'P1', 'Start': 27.19, 'End': 27.19, 'Task': 'Click Object'}, #floor
    {'User': 'P1', 'Start': 28.30, 'End': 30.04, 'Task': 'CB - Query Material'}, #Can you suggest similar materials to gray nonskid tiles for a floor?
    {'User': 'P1', 'Start': 28.42, 'End': 29.05, 'Task': 'Click Object'}, #sofa cushions and pillows
    {'User': 'P1', 'Start': 29.09, 'End': 29.09, 'Task': 'MG - Apply'}, #cotton material 4
    {'User': 'P1', 'Start': 29.20, 'End': 29.26, 'Task': 'Click Object'}, #sofa cushions and pillows 
    {'User': 'P1', 'Start': 29.28, 'End': 29.28, 'Task': 'MG - Apply'}, ##cotton material 7
    {'User': 'P1', 'Start': 29.40, 'End': 29.43, 'Task': 'Scale Texture'}, ##sofa cushions and pillows 
    {'User': 'P1', 'Start': 29.48, 'End': 29.48, 'Task': 'Click Object'}, ##coffee table
    {'User': 'P1', 'Start': 29.58, 'End': 30.51, 'Task': 'MG - Generate'}, ##glass
    {'User': 'P1', 'Start': 30.04, 'End': 30.04, 'Task': 'Click Object'}, ##floor
    {'User': 'P1', 'Start': 30.10, 'End': 30.10, 'Task': 'CB - Apply'}, ##rubber flooring
    {'User': 'P1', 'Start': 30.11, 'End': 30.13, 'Task': 'Scale Texture'}, ##floor
    {'User': 'P1', 'Start': 31.02, 'End': 31.02, 'Task': 'Click Object'}, ##coffee table top
    {'User': 'P1', 'Start': 31.10, 'End': 31.10, 'Task': 'MG - Apply'}, ##glass 3
    {'User': 'P1', 'Start': 31.58, 'End': 33.10, 'Task': 'Render'}, ##glass 4
    {'User': 'P1', 'Start': 33.25, 'End': 34.30, 'Task': 'MG - Generate'}, ##Rubber Flooring, from CB
    {'User': 'P1', 'Start': 33.30, 'End': 33.30, 'Task': 'Click Object'}, ##floor
    {'User': 'P1', 'Start': 33.46, 'End': 33.46, 'Task': 'Click Object'}, ##right fence
    {'User': 'P1', 'Start': 33.51, 'End': 33.51, 'Task': 'Click Object'}, ##pool edge
    {'User': 'P1', 'Start': 34.27, 'End': 34.27, 'Task': 'Click Object'}, ##floor
    {'User': 'P1', 'Start': 34.28, 'End': 34.28, 'Task': 'MG - Apply'}, ##rubber floor 2
    {'User': 'P1', 'Start': 34.29, 'End': 34.29, 'Task': 'MG - Apply'}, ##rubber floor 4
    {'User': 'P1', 'Start': 34.30, 'End': 34.30, 'Task': 'MG - Apply'}, ##rubber floor 6
    {'User': 'P1', 'Start': 34.31, 'End': 34.31, 'Task': 'MG - Apply'}, ##rubber floor 5
    {'User': 'P1', 'Start': 34.32, 'End': 34.32, 'Task': 'MG - Apply'}, ##rubber floor 3
    {'User': 'P1', 'Start': 34.54, 'End': 34.44, 'Task': 'MG - Generate'}, ##Stone flooring
    {'User': 'P1', 'Start': 35.32, 'End': 35.50, 'Task': 'Save'}
    {'User': 'P1', 'Start': 35.52, 'End': 35.52, 'Task': 'Click Object'}, ##floor
    {'User': 'P1', 'Start': 35.55, 'End': 35.55, 'Task': 'MG - Apply'}, ##stone flooring 6
    {'User': 'P1', 'Start': 36.00, 'End': 36.02, 'Task': 'Scale Texture'}, ##stone flooring 4
    {'User': 'P1', 'Start': 36.03, 'End': 37.26, 'Task': 'Render'}, 
    {'User': 'P1', 'Start': 37.30, 'End': 37.47, 'Task': 'Save'}

    {'User': 'P3', 'Start': 47.37, 'End': 47.57, 'Task': 'Click Object'},
    {'User': 'P4', 'Start': 39.05, 'End': 39.30, 'Task': 'CB - Query Material'},
    {'User': 'P4', 'Start': 39.30, 'End': 39.57, 'Task': 'MG - Generate'},
    {'User': 'P4', 'Start': 39.57, 'End': 40.00, 'Task': 'MG - Apply'},
    {'User': 'P5', 'Start': 28.24, 'End': 28.45, 'Task': 'Click Object'},
    {'User': 'P6', 'Start': 42.07, 'End': 42.20, 'Task': 'CB - Query Material'},
    {'User': 'P6', 'Start': 42.57, 'End': 43.07, 'Task': 'MG - Apply'},
    {'User': 'P7', 'Start': 42.00, 'End': 42.20, 'Task': 'Click Object'},
    {'User': 'P8', 'Start': 1.20, 'End': 1.40, 'Task': 'Click Object'},
    {'User': 'P9', 'Start': 45.35, 'End': 45.57, 'Task': 'CB - Query Material'},
    {'User': 'P10', 'Start': 5.00, 'End': 5.20, 'Task': 'Click Object'},
    {'User': 'P11', 'Start': 5.40, 'End': 6.00, 'Task': 'CB - Query Material'},
    {'User': 'P12', 'Start': 48.32, 'End': 49.00, 'Task': 'Click Object'},
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
    'Render': 'yellow',
    'Color Texture': 'purple',
    'CB - Query Material': 'orange',
    'CB - Apply': 'blue',
    'Set Metalness': 'black',
    'Set Roughness': 'brown'

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