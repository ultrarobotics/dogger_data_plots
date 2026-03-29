import os
import math
import pickle
import glob
import re
from collections import OrderedDict


def calculate_total_distance_in_meters(csv_filename):
    """
    Calculates the total traveled distance (only X and Y) from a CSV file in meters.

    Args:
        csv_filename (str): The path to the CSV file.

    Returns:
        float: Total distance traveled in meters.
    """
    positions = []  # List to store (TX, TY) tuples in meters

    try:
        with open(csv_filename, "r") as file:
            lines = file.readlines()

        # Dynamically find the header line starting with 'Frame'
        header_index = None
        for idx, line in enumerate(lines):
            if line.strip().startswith("Frame,Sub Frame"):
                header_index = idx + 2  # Data starts two lines after header
                break

        if header_index is None:
            print(f"Header not found in file: {csv_filename}")
            return 0.0

        for line in lines[header_index:]:
            line = line.strip()
            if not line:
                continue  # Skip empty lines
            parts = line.split(",")

            # Ensure there are enough columns
            if len(parts) < 7:
                print(f"Skipping malformed line in {csv_filename}: {line}")
                continue

            try:
                tx_mm = float(parts[5])
                ty_mm = float(parts[6])
                tx_m = tx_mm / 1000  # Convert millimeters to meters
                ty_m = ty_mm / 1000  # Convert millimeters to meters
                positions.append((tx_m, ty_m))
            except ValueError:
                print(
                    f"Skipping line with invalid float values in {csv_filename}: {line}"
                )
                continue

        if len(positions) < 2:
            print(f"Not enough data points to calculate distance in {csv_filename}.")
            return 0.0

        total_distance_m = 0.0
        for i in range(1, len(positions)):
            x1, y1 = positions[i - 1]
            x2, y2 = positions[i]
            distance = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
            total_distance_m += distance

        return total_distance_m

    except FileNotFoundError:
        print(f"File not found: {csv_filename}")
        return 0.0
    except Exception as e:
        print(f"An error occurred while processing {csv_filename}: {e}")
        return 0.0


def get_ordered_filenames(folder_path):
    """
    Generates a sorted list of filenames based on the desired order:
    nominal1, nominal2, inspection, and searchrescue.

    Args:
        folder_path (str): Path to the folder containing the CSV files.

    Returns:
        list: Ordered list of filenames.
    """
    try:
        # Get all CSV files in the folder
        filenames = [f for f in os.listdir(folder_path) if f.endswith(".csv")]

        # Define custom sorting order for groups
        group_order = {"nominal1": 1, "nominal2": 2, "inspection": 3, "searchrescue": 4}

        # Extract logical groups and numbers for sorting
        def extract_key(filename):
            # Example: doggernominal1run1.csv -> ('nominal1', 1)
            match = re.match(r"dogger(\D+\d*)run(\d+)\.csv", filename)
            if match:
                group = match.group(1)  # E.g., 'nominal1', 'inspection'
                run_number = int(match.group(2))  # E.g., '1', '2', '3'
                # Use group_order to determine priority
                group_priority = group_order.get(group, float("inf"))
                return (group_priority, run_number)
            return (float("inf"), 0)  # Default fallback for unexpected names

        # Sort filenames using the extracted key
        sorted_filenames = sorted(filenames, key=extract_key)

        return sorted_filenames

    except Exception as e:
        print(f"Error occurred: {e}")
        return []


def process_all_csv_files_in_meters(folder_path):
    """
    Processes all CSV files in the specified folder, calculates their total distances in meters,
    and saves the results in a dictionary serialized as a pickle file.

    Args:
        folder_path (str): The path to the folder containing CSV files.

    Returns:
        dict: A dictionary mapping filenames to their total traveled distances in meters.
    """
    distance_dict = {}

    # Get the ordered list of filenames
    sorted_filenames = get_ordered_filenames(folder_path)

    if not sorted_filenames:
        print(f"No CSV files found in folder: {folder_path}")
        return distance_dict

    for filename in sorted_filenames:
        csv_file = os.path.join(folder_path, filename)
        print(f"Processing file: {filename}")
        total_distance = calculate_total_distance_in_meters(csv_file)
        distance_dict[filename] = total_distance
        print(f"Total distance for {filename}: {total_distance:.3f} m")

    return distance_dict


def save_dict_as_pickle(data_dict, pickle_filename):
    """
    Saves the provided dictionary as a pickle file.

    Args:
        data_dict (dict): The dictionary to serialize.
        pickle_filename (str): The path to the output pickle file.
    """
    try:
        # Use OrderedDict to maintain order if necessary
        ordered_dict = OrderedDict(sorted(data_dict.items(), key=lambda x: x[0]))
        with open(pickle_filename, "wb") as pkl_file:
            pickle.dump(ordered_dict, pkl_file)
        print(f"Dictionary successfully saved as {pickle_filename}")
    except Exception as e:
        print(f"Failed to save dictionary as pickle: {e}")


def main():
    folder_name = (
        "data/figure_3/searchandrescue/distances"  # Folder containing CSV files
    )
    current_dir = os.getcwd()
    folder_path = os.path.join(current_dir, folder_name)

    if not os.path.isdir(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # Process all CSV files and get the distance dictionary
    distance_dict = process_all_csv_files_in_meters(folder_path)

    print(distance_dict)

    if not distance_dict:
        print("No distances were calculated. Exiting.")
        return

    # Define the pickle filename
    pickle_filename = os.path.join(folder_path, "distances.pkl")

    # Save the dictionary as a pickle file
    save_dict_as_pickle(distance_dict, pickle_filename)


if __name__ == "__main__":
    main()
