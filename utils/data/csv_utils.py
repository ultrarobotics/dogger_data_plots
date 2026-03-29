import numpy as np


def load_csv(file_path, delimiter=","):
    try:
        return np.genfromtxt(file_path, delimiter=delimiter)
    except Exception as e:
        print(f"Error loading CSV file {file_path}: {e}")
        return None
