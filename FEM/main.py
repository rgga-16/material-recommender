from utils import read_obj_file

file_path = './data/cabinets.obj'
vertices, faces = read_obj_file(file_path)


''' 
Executing "4. Define the material properties of the object, such as Young's modulus and Poisson's ratio, and add them as inputs to the FEM algorithm."
Task 4 response:
As an AI, I do not have a specific material property for the object. The material properties of the object need to be defined by the user based on the physical characteristics of the object. However, I can provide an example Python code snippet that demonstrates how to add the Young's modulus and Poisson's ratio as inputs to the FEM algorithm:
'''

# Define the material properties
youngs_modulus = 210000  # in MPa
poisson_ratio = 0.3

# Add the material properties as inputs to FEM algorithm
from fem import fem_algorithm

obj_file = file_path
force = [100, 0, 0]  # in Newtons
displacement = fem_algorithm(obj_file, youngs_modulus, poisson_ratio, force)

print(displacement)

'''
In the above code snippet, we define the Young's modulus and Poisson's 
ratio and then pass them as inputs to the FEM algorithm along with the .obj file and the force applied. 
The FEM algorithm then calculates the displacement of the object under the applied force, which is printed to the console.
'''