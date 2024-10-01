import pandas as pd
import os 
import numpy as np
import krippendorff

# Specify the file path
dir = './experiment_data/Expert Validation 2'
file_path = os.path.join(dir, 'Vargas2.csv')

# Read the .csv file into a pandas dataframe
orig_data = pd.read_csv(file_path)

# # Remove the first column and the first row from data
# data_no_exp1 = orig_data.iloc[1:] #Remove the first row


data = orig_data.iloc[:, 1:] #Remove the first row and the first column (Last Name)
data = data.replace('Valid', 1)
data = data.replace('Invalid', 0)

data = data.dropna(axis='columns', how='all')
data = data.dropna(axis='rows', how='all')

data_list = data.values.tolist()
data_np = np.array(data_list)   

alpha = krippendorff.alpha(reliability_data=data_np, level_of_measurement='nominal')
print(f"Krippendorff's alpha: {alpha}")
pass