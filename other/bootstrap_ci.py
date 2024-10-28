import csv
import numpy as np
np.random.seed(42)
import matplotlib.pyplot as plt


nasatlx_scores = {
    'NASA-TLX': [61.6666667, 26, 52, 60.6666667, 21.6666667, 51.3333333, 57.6666667, 53.3333333, 27.6666667, 58.6666667, 50.3333333],
    'Mental Demand': [85, 10, 85, 85, 5, 80, 80, 55, 10, 20, 35],
    'Temporal Demand': [75, 5, 70, 15, 30, 85, 55, 45, 5, 70, 60],
    'Performance': [15, 5, 60, 80, 5, 15, 35, 50, 75, 65, 60],
    'Effort': [55, 80, 10, 65, 40, 75, 55, 45, 15, 35, 45],
    'Frustration': [80, 5, 30, 70, 30, 30, 35, 65, 85, 60, 55]
}

csi_scores = {
    'CSI': [43.66666667, 97, 74.66666667, 77.33333333, 90, 81.66666667, 52.66666667, 81.33333333, 67.66666667, 71.66666667, 63.33333333],
    'Enjoyment': [10, 20, 12, 13, 20, 17, 15, 16, 17, 16, 15],
    'Exploration': [9, 19, 20, 16, 20, 17, 12, 18, 17, 17, 15],
    'Expressiveness': [9, 19, 14, 17, 16, 16, 10, 15, 14, 14, 12],
    'Immersion': [11, 20, 9, 15, 15, 15, 10, 16, 11, 8, 16],
    'Results Worth Effort': [6, 20, 16, 16, 18, 16, 9, 16, 10, 13, 9]
}

def bootstrap_confidence_interval(data, num_samples=10000, confidence_level=0.95):
    # Convert data to numpy array for easier manipulation
    data = np.array(data)
    
    # Create bootstrap samples and calculate means
    bootstrap_means = []
    for _ in range(num_samples):
        bootstrap_sample = np.random.choice(data, size=len(data), replace=True)
        bootstrap_means.append(np.mean(bootstrap_sample))
    
    # Calculate the lower and upper bounds of the confidence interval
    lower_bound = np.percentile(bootstrap_means, (1 - confidence_level) / 2 * 100)
    upper_bound = np.percentile(bootstrap_means, (1 + confidence_level) / 2 * 100)
    
    return lower_bound, upper_bound, bootstrap_means

# Open a CSV file to write the results
with open('nasatlx_bootstrap_confidence_intervals.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(['Dimension', 'Lower Bound', 'Upper Bound'])


    for key, value in nasatlx_scores.items():
        scores = value; dimension = key
        
        lower, upper, bootstrap_means = bootstrap_confidence_interval(scores)
        print(f"95% Confidence Interval for {key}: {bootstrap_confidence_interval(scores)}")

        # Save the results to the CSV file
        writer.writerow([dimension, lower, upper])

        # ----------------------------------------------------

        # Plotting the bootstrap distribution
        plt.hist(bootstrap_means, bins=50, color='lightcoral', alpha=0.7)
        plt.axvline(lower, color='red', linestyle='--', label=f'Lower Bound ({lower:.2f})')
        plt.axvline(upper, color='red', linestyle='--', label=f'Upper Bound ({upper:.2f})')
        plt.axvline(np.mean(scores), color='black', linestyle='-', label=f'Mean ({np.mean(scores):.2f})')
        plt.xlabel(f'Mean {key} Score')
        plt.ylabel('Frequency')
        plt.title(f'Bootstrap Distribution of {key} Means')
        plt.legend()
        # plt.show()
        plt.savefig(f'nasatlx_bootstrap_{key}.png')
        plt.clf()
    
    file.close()



# Open a CSV file to write the results
with open('csi_bootstrap_confidence_intervals.csv', mode='w', newline='') as file:
    writer = csv.writer(file)
    # Write the header
    writer.writerow(['Dimension', 'Lower Bound', 'Upper Bound'])

    for key, value in csi_scores.items():
        scores = value; dimension = key
        
        lower, upper, bootstrap_means = bootstrap_confidence_interval(scores)
        print(f"95% Confidence Interval for {key}: {bootstrap_confidence_interval(scores)}")

        # Save the results to the CSV file
        writer.writerow([dimension, lower, upper])

        # ----------------------------------------------------

        # Plotting the bootstrap distribution
        plt.hist(bootstrap_means, bins=50, color='skyblue', alpha=0.7)
        plt.axvline(lower, color='red', linestyle='--', label=f'Lower Bound ({lower:.2f})')
        plt.axvline(upper, color='red', linestyle='--', label=f'Upper Bound ({upper:.2f})')
        plt.axvline(np.mean(scores), color='black', linestyle='-', label=f'Mean ({np.mean(scores):.2f})')
        plt.xlabel(f'Mean {key} Score')
        plt.ylabel('Frequency')
        plt.title(f'Bootstrap Distribution of {key} Means')
        plt.legend()
        # plt.show()
        plt.savefig(f'csi_bootstrap_{key}.png')
        plt.clf()

    file.close()




