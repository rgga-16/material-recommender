'''
To execute Task 1, I will implement a Python function that can parse .obj files and extract the necessary information such as vertex data and connectivity information for finite element analysis. Here is the function:
'''


import numpy as np

def parse_obj_file(obj_path):
    vertices = []
    elements = []

    with open(obj_path, 'r') as obj_file:
        for line in obj_file:
            tokens = line.split()

            if not tokens:
                continue

            if tokens[0] == 'v':
                # vertex coordinate
                vertices.append([float(val) for val in tokens[1:]])
            elif tokens[0] == 'f':
                # face/element definition
                face = []
                for val in tokens[1:]:
                    # Split val by '/' to support vertex/texture/normal format
                    vertex_index = val.split('/')[0]
                    face.append(int(vertex_index) - 1)  # Convert to 0-based index
                elements.append(face)

    vertices = np.array(vertices)
    elements = np.array(elements)

    return vertices, elements


if __name__=="__main__":
    # Example usage
    obj_path = './data/cabinets.obj'
    vertices, elements = parse_obj_file(obj_path)
    print('Vertices:\n', vertices)
    print('\nElements:\n', elements)