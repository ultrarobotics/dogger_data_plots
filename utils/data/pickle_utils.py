import pickle
import os


def load_pickle(file_path):
    """Load a pickle file and return its content."""
    try:
        with open(file_path, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        print(f"Pickle file not found: {file_path}")
        return None
    except Exception as e:
        print(f"Error loading pickle file {file_path}: {e}")
        return None


def save_pickle(data, file_path):
    """Save data to a pickle file."""
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    try:
        with open(file_path, "wb") as f:
            pickle.dump(data, f)
        print(f"Saved pickle file: {file_path}")
    except Exception as e:
        print(f"Error saving pickle file {file_path}: {e}")
