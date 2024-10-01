import pandas as pd
import os 
import numpy as np
import statsmodels.stats.inter_rater as irr

# Specify the file path
dir = './experiment_data/Expert Validation 2'
file_path = os.path.join(dir, 'Vargas2.csv')

# Read the .csv file into a pandas dataframe
orig_data = pd.read_csv(file_path)


data = orig_data.iloc[:, 1:] #Remove the first expert and the first column (Last Name)
data = data.drop(index=[0,data.index[-1]]) #Remove the first row and the last row
data = data.replace('Valid', 1)
data = data.replace('Invalid', 0)

data = data.dropna(axis='columns', how='all')
data = data.dropna(axis='rows', how='all')

data_list = data.values.tolist()
data_np = np.array(data_list)   
data_np = data_np.transpose()

# Aggregate the ratings
table, categories = irr.aggregate_raters(data_np)

# Compute Fleiss' Kappa
kappa = irr.fleiss_kappa(table)

print(f"Fleiss' kappa: {kappa}")
pass