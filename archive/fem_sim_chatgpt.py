'''
Embarking on a new goal:Create a Python code that inputs a .obj file and performs FEM on it when applying a certain force.

Added task:1. Develop a Python script that can read a .obj file and extract its vertices and faces data.
Added task:2. Implement a FEM algorithm in Python that calculates the displacement of each vertex based on the applied force and the material properties of the object.
Added task:3. Integrate the vertex displacement data into a visualization tool, such as Paraview, to generate a visual representation of the deformed object.
Added task:4. Define the material properties of the object, such as Young's modulus and Poisson's ratio, and add them as inputs to the FEM algorithm.
'''

# Executing "1. Develop a Python script that can read a .obj file and extract its vertices and faces data."

import numpy as np

def read_obj_file(file_path):
    vertices = []
    faces = []
    with open(file_path, 'r') as f:
        for line in f:
            if line.startswith('v '):
                vertex = list(map(float, line[2:].strip().split()))
                vertices.append(vertex)
            elif line.startswith('f '):
                face = list(map(int, line[2:].strip().split()))
                face = [i - 1 for i in face]  # obj file indices start from 1
                faces.append(face)
    vertices = np.array(vertices)
    faces = np.array(faces)
    return vertices, faces

# To use this function, simply call it with the file path of the .obj file as the argument, like so:
file_path = './data/3d_models/bedroom/bed/mattress.obj'
vertices, faces = read_obj_file(file_path)

'''
This will return two numpy arrays: vertices, 
which contains the coordinates of each vertex in the .obj file, and faces, 
which contains the vertex indices that make up each face in the .obj file.
You can use these arrays as inputs for your FEM algorithm to perform analysis on the object.
'''

############################################################################################################################################################################

# Executing "2. Implement a FEM algorithm in Python that calculates the displacement of each vertex based on the applied force and the material properties of the object."

# Define function for FEM algorithm
def fem_algorithm(vertices, edges, faces, force, material_properties):
    # Initialize variables
    displacement = np.zeros(vertices.shape)
    stiffness_matrix = np.zeros((vertices.shape[0]*3, vertices.shape[0]*3))
    # Calculate stiffness matrix for the object
    for face in faces:
        # Get vertices of the face
        v1, v2, v3 = vertices[face[0]], vertices[face[1]], vertices[face[2]]
        # Calculate area of the face using cross product of two edges
        area = np.cross(v2 - v1, v3 - v1) / 2
        # Calculate element stiffness matrix using material properties and area
        element_stiffness_matrix = material_properties * area / 6 *\
            np.array([[2, 1, 1, 0, 0, 0],
                    [1, 2, 1, 0, 0, 0],
                    [1, 1, 2, 0, 0, 0],
                    [0, 0, 0, 2, 1, 1],
                    [0, 0, 0, 1, 2, 1],
                    [0, 0, 0, 1, 1, 2]])
        # Assemble element stiffness matrix to global stiffness matrix
        for i in range(3):
            for j in range(3):
                stiffness_matrix[face[i]*3:face[i]*3+3, face[j]*3:face[j]*3+3] += \
                    element_stiffness_matrix[i*3:i*3+3, j*3:j*3+3]
    # Apply force to the object
    force_vector = np.zeros((vertices.shape[0]*3,))
    force_vector[force[0]*3] = force[1]
    force_vector[force[0]*3+1] = force[2]
    force_vector[force[0]*3+2] = force[3]
    # Solve for displacement using matrix inversion
    displacement_vector = np.linalg.solve(stiffness_matrix, force_vector)
    for i in range(vertices.shape[0]):
        displacement[i] = displacement_vector[i*3:i*3+3]
    return displacement

'''
The fem_algorithm function takes in four inputs: vertices (an array of shape (n, 3) where n is the number of vertices in the object), edges (an array of shape (m, 2) where m is the number of edges in the object), faces (an array of shape (p, 3) where p is the number of faces in the object), force (a tuple containing the index of the vertex where the force is applied and the force vector in the form (index, x, y, z)), and material_properties (a scalar representing the material properties of the object).
The function first initializes the displacement and stiffness matrix variables to zero. It then calculates the stiffness matrix for the object by iterating through each face and calculating the area and element stiffness matrix. The element stiffness matrix is then assembled to the global stiffness matrix. Next, the function applies the force to the object by creating a force vector and inserting
'''