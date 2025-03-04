import pandas as pd
import os 
import numpy as np
import krippendorff

# Specify the file path
dir = './experiment_data/Expert Validation/Krippendorff Alpha'
file_path = os.path.join(dir, 'Use and Safety.csv')

# Read the .csv file into a pandas dataframe
orig_data = pd.read_csv(file_path)

# # Remove the first column and the first row from data
# data_no_exp1 = orig_data.iloc[1:] #Remove the first row (j*****)


data = orig_data.iloc[1:, 1:] #Remove the first row (j*****) and the first column (Email)
data = data.replace('Unsuitable', 1)
data = data.replace('Somewhat unsuitable', 2)
data = data.replace('Unsure', 3)
data = data.replace('Somewhat suitable', 4)
data = data.replace('Suitable', 5)

data = data.dropna(axis='columns', how='all')
data = data.dropna(axis='rows', how='all')

data_list = data.values.tolist()
data_np = np.array(data_list)   

al = krippendorff.alpha(reliability_data=data_np, level_of_measurement='ordinal')
print(f"Krippendorff's alpha: {al}")
pass