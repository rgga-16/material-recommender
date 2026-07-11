import pandas as pd
import numpy as np
import sys

def gwets_ac1_binary(df):
    """
    Compute Gwet's AC1 for multi-rater, binary (0/1) nominal data.
    
    Parameters
    ----------
    df : pd.DataFrame
        Shape (R, n). R = number of raters (rows),
        n = number of items (columns).
        Each cell is 0 or 1.
        
    Returns
    -------
    float
        Gwet's AC1 estimate.
    """
    R, n = df.shape
    
    # 1) Compute item-level agreement for each item.
    #    For each column: proportion of 1's = p_i
    #    Then item-level agreement A_i = p_i^2 + (1 - p_i)^2
    A_per_item = []
    for col in df.columns:
        # Drop missing if any (should not be the case in 0/1 data, but just in case)
        column_data = df[col].dropna()
        p_i = column_data.mean()
        A_i = p_i**2 + (1 - p_i)**2
        A_per_item.append(A_i)
    
    # Observed agreement (P_o) = average of item-level agreements
    P_o = np.mean(A_per_item)
    
    # 2) Compute chance agreement (P_e) using a simplified Gwet-like approach.
    #    For binary data, a common approach:
    #       d_i = p_i * (1 - p_i)  (the proportion of 1–0 split for item i)
    #    Then the average mismatch across items is D = mean(d_i).
    #    For 2 raters, chance disagreement would be 2*D, so chance agreement = 1 - 2*D.
    #    For >2 raters, the exact formula is more involved, but this is a reasonable approximation.
    
    d_values = []
    for col in df.columns:
        p_i = df[col].mean()
        d_i = p_i * (1 - p_i)
        d_values.append(d_i)
    
    D = np.mean(d_values)  # average mismatch factor
    P_e = 1 - 2*D          # approximate chance agreement
    
    # 3) Gwet’s AC1
    #    AC1 = (P_o - P_e) / (1 - P_e), provided (1 - P_e) != 0
    if abs(1 - P_e) < 1e-9:
        # Edge case: if everything is in the same category, P_e might be ~1
        return float('nan')
    AC1 = (P_o - P_e) / (1.0 - P_e)
    return AC1


def main():
    # # Expect the CSV filename as a command-line argument
    # if len(sys.argv) < 2:
    #     print("Usage: python gwets_ac1.py <filename.csv>")
    #     sys.exit(1)
    
    # filename = sys.argv[1]
    
    # Read CSV into a DataFrame
    # If your CSV has an extra column for "Rater ID", either drop it
    # or specify which columns to use, e.g., usecols=[1,2,3,...]
    df = pd.read_csv("./experiment_data/Full User Study/Experiment 2/Feedback Module/Suggestions-durability_gwets.csv")
    
    df = df.iloc[:, 1:] #Remove the the first column (Last Name)
    df = df.replace('Valid', 1)
    df = df.replace('Not valid', 0)

    df = df.dropna(axis='columns', how='all')
    df = df.dropna(axis='rows', how='all')


    # Convert all columns to numeric (in case of strings)
    df = df.apply(pd.to_numeric, errors='coerce')
    
    # df.shape: (R, n) with each cell 0/1
    # If your data are oriented differently (items as rows, raters as columns),
    # you might need df = df.T to transpose.
    
    # Calculate Gwet's AC1
    ac1_value = gwets_ac1_binary(df)
    
    print("Gwet's AC1 =", ac1_value)


if __name__ == "__main__":
    main()


