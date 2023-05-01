'''
Executing "Task 4: Integrate FEniCS library for FEM analysis on the extracted vertex and element data, and apply the specified force."
To integrate the FEniCS library for FEM analysis on the extracted vertex and element data, and apply the specified force, you can use the following Python code:
'''

import fenics
import numpy as np
import meshio

def read_obj_file(file_path):
    with open(file_path, "r") as file:
        lines = file.readlines()

    vertices = []
    elements = []

    for line in lines:
        data = line.split()
        if not data:
            continue
        if data[0] == 'v':
            vertices.append([float(v) for v in data[1:]])
        elif data[0] == 'f':
            elements.append([int(e.split('/')[0]) - 1 for e in data[1:]])

    return np.array(vertices), np.array(elements)

def perform_fem_analysis(obj_file_path, force):
    vertices, elements = read_obj_file(obj_file_path)

    mesh = meshio.Mesh(vertices, {"triangle": elements})
    meshio.write("temp_mesh.xdmf", mesh)

    mesh = fenics.Mesh()
    with fenics.XDMFFile("temp_mesh.xdmf") as infile:
        infile.read(mesh)

    V = fenics.VectorFunctionSpace(mesh, "P", 1)

    def boundary(x, on_boundary):
        return on_boundary

    bc = fenics.DirichletBC(V, fenics.Constant((0.0, 0.0, 0.0)), boundary)

    u = fenics.TrialFunction(V)
    v = fenics.TestFunction(V)

    a = fenics.inner(fenics.grad(u), fenics.grad(v)) * fenics.dx
    L = fenics.dot(force, v) * fenics.dx

    u = fenics.Function(V)
    fenics.solve(a == L, u, bc)

    return u

'''
Here, we have a perform_fem_analysis function that takes the path to the .obj file and the force being applied. First, we read the .obj file to extract the vertices and elements using the read_obj_file function. Then, we create a FEniCS mesh and perform FEM analysis on it. The resulting function u contains the displacement values after applying the force.
However, visualization of the effect is not included in this code snippet. To visualize the effect of the force being applied onto the 3D model, I would recommend using tools like Paraview or Mayavi for loading the mesh and visualizing the results. You can export the results in the VTK format, for example, and then use those tools to visualize them.
'''