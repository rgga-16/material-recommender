'''
MCDM stands for Multi-Criteria Decision Making, which is a branch of operations research that deals with decision-making problems involving multiple, usually conflicting criteria. It involves evaluating and choosing the best option from a set of alternatives based on several criteria. MCDM methods are widely used in various fields such as business, engineering, environmental management, and public policy to support complex decision-making processes.

TOPSIS, which stands for Technique for Order of Preference by Similarity to Ideal Solution, is a specific MCDM method. It was developed by Ching-Lai Hwang and Yoon in 1981. TOPSIS is based on the concept that the chosen alternative should have the shortest geometric distance from the positive ideal solution (PIS) and the farthest geometric distance from the negative ideal solution (NIS).

The PIS is a hypothetical alternative that has the best performance for all criteria, while the NIS has the worst performance for all criteria. The steps involved in the TOPSIS method typically include:

1. Establishing the decision matrix, which includes the alternatives and the criteria for evaluation.
2. Normalizing the decision matrix to make the criteria comparable, often using a vector normalization method.
3. Assigning weights to the criteria to reflect their relative importance in the decision-making process.
4. Determining the PIS and NIS based on the weighted normalized decision matrix.
5. Calculating the Euclidean distance of each alternative from the PIS and NIS.
6. Calculating the relative closeness of each alternative to the PIS, which is a measure of the performance of each alternative.
7. Ranking the alternatives based on their relative closeness to the PIS, with the alternative closest to the PIS being the preferred choice.

TOPSIS is popular due to its simplicity, computational efficiency, and ability to provide a clear rationale for decision-making. It is particularly useful when decision-makers need to evaluate alternatives based on multiple, often conflicting criteria.

To implement a TOPSIS algorithm for material selection in Python, we first need to define the criteria for selection and the alternatives (materials) to be evaluated. For this example, let's assume we have four materials to choose from and three criteria: strength, cost, and weight. The goal is to select the material with the highest strength, lowest cost, and lowest weight.

Here's a step-by-step implementation of the TOPSIS algorithm in Python:
'''

import numpy as np

# Step 1: Create the decision matrix
# Each row represents an alternative (material), and each column represents a criterion
# For simplicity, assume the values are already normalized (e.g., strength in MPa, cost in $/kg, weight in kg/m^3)
decision_matrix = np.array([
    [0.8, 0.6, 0.3],  # Material 1
    [0.9, 0.8, 0.4],  # Material 2
    [0.7, 0.9, 0.5],  # Material 3
    [0.6, 0.5, 0.2],  # Material 4
])

# Step 2: Normalize the decision matrix
# Here we use the vector normalization method
norm_decision_matrix = decision_matrix / np.sqrt((decision_matrix**2).sum(axis=0))

# Step 3: Assign weights to the criteria
# Let's assume strength is twice as important as cost and weight
weights = np.array([0.5, 0.25, 0.25])

# Step 4: Calculate the weighted normalized decision matrix
weighted_norm_matrix = norm_decision_matrix * weights

# Step 5: Determine the positive ideal solution (PIS) and negative ideal solution (NIS)
pis = weighted_norm_matrix.max(axis=0)
nis = weighted_norm_matrix.min(axis=0)

# Step 6: Calculate the Euclidean distance from each alternative to the PIS and NIS
distance_to_pis = np.sqrt(((weighted_norm_matrix - pis) ** 2).sum(axis=1))
distance_to_nis = np.sqrt(((weighted_norm_matrix - nis) ** 2).sum(axis=1))

# Step 7: Calculate the relative closeness to the PIS
relative_closeness = distance_to_nis / (distance_to_nis + distance_to_pis)

# Step 8: Rank the alternatives based on their relative closeness to the PIS
ranking = np.argsort(relative_closeness)[::-1] + 1  # Add 1 to start ranking from 1 instead of 0

# Display the results
print("Relative Closeness:", relative_closeness)
print("Ranking:", ranking)

# The best material is the one with the highest relative closeness
best_material_index = np.argmax(relative_closeness)
print(f"The best material is Material {best_material_index + 1}")

'''
This code will output the relative closeness of each material to the ideal solution and rank them accordingly. The material with the highest relative closeness is considered the best choice according to the TOPSIS method.

Please note that in a real-world scenario, the decision matrix values would need to be normalized based on the actual data, and the weights would be determined by the decision-makers based on the importance of each criterion. The criteria might also need to be maximized or minimized accordingly (e.g., cost should be minimized, while strength should be maximized).
'''