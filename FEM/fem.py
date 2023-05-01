'''
Executing "Task 2: Implement FEM algorithm in Python to analyze the 3D model, considering the specific force to be applied."

To implement the FEM algorithm and analyze the 3D model with a specific force applied, you can use the following Python code:
'''

import numpy as np
import pyvista as pv
from pyvista import examples
from scipy.sparse.linalg import spsolve
import trimesh

def input_obj_file(file_path):
    mesh = trimesh.load(file_path)
    nodes = mesh.vertices
    elements = mesh.faces
    return nodes, elements

def create_stiffness_matrix(nodes, elements, youngs_modulus, poisson_ratio):
    n_nodes = len(nodes)
    K = np.zeros((n_nodes * 3, n_nodes * 3))

    for element in elements:
        # Calculate D, the constitutive matrix
        D = (youngs_modulus / (1 - poisson_ratio ** 2)) * np.array([[1, poisson_ratio, 0], 
                [poisson_ratio, 1, 0], 
                [0, 0, 0.5 * (1 - poisson_ratio)]])
        
        # Calculate B, the strain-displacement matrix
        B = np.zeros((3, 9))
        for i in range(3):
            j = 0 if i == 2 else i + 1
            x_diff = nodes[element[j], 0] - nodes[element[i], 0]
            y_diff = nodes[element[j], 1] - nodes[element[i], 1]
            z_diff = nodes[element[j], 2] - nodes[element[i], 2]
            B[:, i * 3:(i + 1) * 3] = np.column_stack((x_diff, y_diff, z_diff))

        # Calculate volume
        volume = np.abs(np.dot(nodes[element[0]] - nodes[element[1]], np.cross(nodes[element[1]] - nodes[element[2]], nodes[element[2]] - nodes[element[0]]))) / 6

        # Assemble stiffness matrix
        Ke = volume * B.T @ D @ B
        for i in range(3):
            for j in range(3):
                K[3 * element[i]:3 * element[i] + 3, 3 * element[j]:3 * element[j] + 3] += Ke[i * 3:(i + 1) * 3, j * 3:(j + 1) * 3]

    return K

def apply_boundary_conditions(K, force_vector, fixed_nodes):
    all_nodes = list(range(K.shape[0] // 3))
    free_nodes = list(set(all_nodes) - set(fixed_nodes))

    K_reduced = K[np.ix_(free_nodes * 3, free_nodes * 3)] # Reduced stiffness matrix
    force_vector_reduced = force_vector[free_nodes * 3]  # Reduced force vector

    return K_reduced, force_vector_reduced, free_nodes * 3

def solve_displacements(K_reduced, force_vector_reduced):
    displacements = spsolve(K_reduced, force_vector_reduced)
    return displacements

def visualize_mesh(nodes, elements, displacements, scale=100):
    warped_nodes = nodes + displacements.reshape(-1, 3) * scale
    mesh = pv.PolyData(warped_nodes, pv.cells_from_trimesh_2D(elements))
    plotter = pv.Plotter()
    plotter.add_mesh(mesh, show_edges=True, scalars=np.linalg.norm(displacements, axis=1), cmap="coolwarm")
    plotter.add_scalar

