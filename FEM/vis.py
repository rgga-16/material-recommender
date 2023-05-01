'''
Executing "Task 3: Create a visualization function to display the 3D model, force applied, and the resulting displacement within the model after the FEM analysis."
To create the visualization function, we will use the matplotlib library for creating 3D plots and visualizing the force and displacement within the model after the FEM analysis. Assuming that we have the necessary data from the FEM analysis (such as vertices, elements, force vector, and displacement vector), the visualize_fem_analysis function should look like this:
'''
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.mplot3d.art3d import Poly3DCollection

def visualize_fem_analysis(vertices, elements, force_vector, displacement_vector, scale_factor=1):
    """
    Function to visualize the FEM analysis results on a given model.
    
    Parameters:
    - vertices: list of vertex coordinates (numpy array)
    - elements: list of elements (numpy array)
    - force_vector: force vector applied to the model (numpy array)
    - displacement_vector: resulting displacement of vertices after FEM analysis (numpy array)
    - scale_factor: factor to scale the displacement to make it more visible (default = 1)
    """
    # Update the vertices with the displacement vector
    displaced_vertices = vertices + scale_factor * displacement_vector

    # Create a 3D plot
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Plot the original model and the displaced model
    for element in elements:
        # Get the vertices of the element
        vtx = vertices[element]

        # Create a 3D polygon and add it to the plot
        poly = Poly3DCollection([vtx], alpha=0.5, facecolor='#800000')
        ax.add_collection3d(poly)

        # Get the displaced vertices of the element
        displaced_vtx = displaced_vertices[element]

        # Create a 3D polygon for the displaced element and add it to the plot
        displaced_poly = Poly3DCollection([displaced_vtx], alpha=0.5, facecolor='#0000FF')
        ax.add_collection3d(displaced_poly)

    # Define the force vector arrow
    force_arrow = plt.Arrow3D(force_vector)

    # Add the force vector arrow to the plot
    ax.add_artist(force_arrow)

    # Set the plot limits and labels
    ax.set_xlim(np.min(vertices[:, 0]), np.max(vertices[:, 0]))
    ax.set_ylim(np.min(vertices[:, 1]), np.max(vertices[:, 1]))
    ax.set_zlim(np.min(vertices[:, 2]), np.max(vertices[:, 2]))
    ax.set_xlabel("X-axis")
    ax.set_ylabel("Y-axis")
    ax.set_zlabel("Z-axis")

    # Show the plot
    plt.show()

'''
This visualize_fem_analysis function takes the vertices, elements, force vector, displacement vector, and an optional scale factor as inputs. 
It calculates the displaced vertices based on the displacement vector, and then creates a 3D plot showing both the original and the displaced models along with the force vector arrow. 
Note that in this example, we're using a separate library (mpl_toolkits.mplot3d.art3d.Poly3DCollection) to draw the 3D polygon for each element in the model.
Before using this function, you will need to perform the FEM analysis and obtain the force vector and displacement vector. 
The scale factor can be adjusted to make the displacement more visible in the plot.
'''

############################################################################################################################################################################################################################

'''
Executing "Task 5: Utilize visualization libraries such as VTK or PyVista to display the 3D model, applied force, and resulting displacements after FEM analysis."
To execute Task 5, I will provide a Python code snippet that utilizes PyVista library to visualize the 3D model, applied force, and resulting displacements after FEM analysis. Make sure to install the required libraries using pip install pyvista and pip install numpy.
'''

import pyvista as pv
import numpy as np

def visualize_fem_results(mesh_file, node_displacements, force_vector, force_position):
    """
    Visualize .obj file and the FEM results using PyVista.

    :param mesh_file: str, path to the .obj file
    :param node_displacements: numpy array, the displacement values for each node
    :param force_vector: numpy array, force vector applied [Fx, Fy, Fz]
    :param force_position: numpy array, position of force application [Px, Py, Pz]
    """

    # Read the mesh from .obj file
    mesh = pv.read(mesh_file)

    # Create a plotter
    plotter = pv.Plotter()

    # Add the original mesh to the plotter
    plotter.add_mesh(mesh, color='gray', show_edges=True, opacity=0.5, label='Original Mesh')

    # Apply the node displacements to the mesh and visualize
    mesh.points += node_displacements
    plotter.add_mesh(mesh, color='blue', show_edges=True, label='Deformed Mesh')

    # Add the force vector at the application point
    force_glyph = pv.Arrow(start=force_position, direction=force_vector, scale=5)
    plotter.add_mesh(force_glyph, color='red', label='Applied Force')

    # Set background color and size
    plotter.background_color = 'white'
    plotter.set_plot_theme('document')

    # Set camera position for better viewing
    plotter.view_xy()

    # Add an informative legend
    plotter.add_legend()

    # Show the plot
    plotter.show()

if __name__=="__main__":
    # Example usage
    mesh_file = './data/cabinets.obj'
    node_displacements = np.random.rand(8, 3)  # Example displacement values, replace with actual FEM results
    force_vector = np.array([1, 0, 0])
    force_position = np.array([0, 0, 0])

    visualize_fem_results(mesh_file, node_displacements, force_vector, force_position)