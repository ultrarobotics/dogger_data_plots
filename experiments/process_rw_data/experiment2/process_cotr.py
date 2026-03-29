import pickle
import numpy as np
import os
import re
import bisect
from collections import OrderedDict


def calculate_system_energy(power_watt=16.2, time_seconds=120):
    """
    Calculate the system energy consumption in Wh.

    Args:
        power_watt (float): Power consumption in watts.
        time_seconds (float): Time in seconds.

    Returns:
        float: Energy consumption in Wh.
    """
    energy_wh = power_watt * (time_seconds / 3600)  # Convert seconds to hours
    return energy_wh


system_energy = calculate_system_energy()  # System energy consumption in Wh

# =======================
# Configuration
# =======================

system_energy = calculate_system_energy()  # System energy consumption in Wh

# =======================
# Configuration
# =======================


def load_pickle_file(pickle_path):
    """
    Loads a pickle file and returns its content.

    Args:
        pickle_path (str): Path to the pickle file.

    Returns:
        Any: The content of the pickle file.
    """
    try:
        with open(pickle_path, "rb") as f:
            data = pickle.load(f)
        print(f"Loaded pickle file: {pickle_path}")
        return data
    except FileNotFoundError:
        print(f"Pickle file not found: {pickle_path}")
        return None
    except Exception as e:
        print(f"Error loading pickle file {pickle_path}: {e}")
        return None


def sort_distances_by_order(distances):
    """
    Sorts the distances dictionary into the desired order:
    nominal1, nominal2, inspection, searchrescue.

    Args:
        distances (dict): Dictionary containing distances with filenames as keys.

    Returns:
        OrderedDict: Sorted dictionary in the desired order.
    """
    group_order = {"nominal1": 1, "nominal2": 2, "inspection": 3, "searchrescue": 4}

    def extract_key(filename):
        # Example: doggernominal1run1.csv -> ('nominal1', 1)
        match = re.match(r"dogger(\D+\d*)run(\d+)\.csv", filename)
        if match:
            group = match.group(1)  # E.g., 'nominal1', 'inspection'
            run_number = int(match.group(2))  # E.g., '1', '2', '3'
            group_priority = group_order.get(group, float("inf"))
            return (group_priority, run_number)
        return (float("inf"), 0)

    sorted_distances = OrderedDict(
        sorted(distances.items(), key=lambda x: extract_key(x[0]))
    )
    return sorted_distances


# Define a list of pickle file paths you want to visualize
file_paths = [
    "data/figure_3/searchandrescue/energy_log_20241128111442.pkl",  # nominal1 run1
    "data/figure_3/searchandrescue/energy_log_20241128112136.pkl",  # nominal1 run2
    "data/figure_3/searchandrescue/energy_log_20241128112640.pkl",  # nominal1 run3
    "data/figure_3/searchandrescue/energy_log_20241128113009.pkl",  # nominal1 run4
    "data/figure_3/searchandrescue/energy_log_20241202113842.pkl",  # nominal2 run1
    "data/figure_3/searchandrescue/energy_log_20241202114456.pkl",  # nominal2 run2
    "data/figure_3/searchandrescue/energy_log_20241202114806.pkl",  # nominal2 run3
    "data/figure_3/searchandrescue/energy_log_20241202115126.pkl",  # nominal2 run4
    "data/figure_3/searchandrescue/energy_log_20241202172116.pkl",  # inspection run1
    "data/figure_3/searchandrescue/energy_log_20241203125834.pkl",  # inspection run2
    "data/figure_3/searchandrescue/energy_log_20241203130333.pkl",  # inspection run3
    "data/figure_3/searchandrescue/energy_log_20241203130719.pkl",  # inspection run4
    "data/figure_3/searchandrescue/energy_log_20241203173752.pkl",  # searchrescue run1
    "data/figure_3/searchandrescue/energy_log_20241203174155.pkl",  # searchrescue run2
    "data/figure_3/searchandrescue/energy_log_20241203174514.pkl",  # searchrescue run3
    "data/figure_3/searchandrescue/energy_log_20241203174830.pkl",  # searchrescue run4
]

distance_file = ["data/figure_3/searchandrescue/distances/distances.pkl"]

# Load distances from pickle and sort them in the desired order
distances = load_pickle_file(distance_file[0])
if distances:
    distances = sort_distances_by_order(distances)
    print("Sorted distances:", distances)

# Convert to a list in the sorted order
distances = list(distances.values())
print("Distances list:", distances)

# Define the heatloss and mechanical power constants
dt = 0.04  # seconds
heatloss_constant = 0.5299
mechanical_power_constant = 0.6091
power_system = 16.2  # system power consumption in Watts, experimentally validated

# Initialize lists to store data from all files and all runs
all_runs = []  # Each element corresponds to a file and contains a list of runs

num_intervals = 1

# =======================
# Define Design Names Mapping
# =======================

# Define a mapping from each pickle file's basename to a design name
design_names_mapping = {
    "data/figure_3/searchandrescue/energy_log_20241128111442.pkl": "nominal_design_1",
    "data/figure_3/searchandrescue/energy_log_20241128112136.pkl": "nominal_design_1",
    "data/figure_3/searchandrescue/energy_log_20241128112640.pkl": "nominal_design_1",
    "data/figure_3/searchandrescue/energy_log_20241128113009.pkl": "nominal_design_1",
    "data/figure_3/searchandrescue/energy_log_20241202113842.pkl": "nominal_design_2",
    "data/figure_3/searchandrescue/energy_log_20241202114456.pkl": "nominal_design_2",
    "data/figure_3/searchandrescue/energy_log_20241202114806.pkl": "nominal_design_2",
    "data/figure_3/searchandrescue/energy_log_20241202115126.pkl": "nominal_design_2",
    "data/figure_3/searchandrescue/energy_log_20241202172116.pkl": "optimized_design_exp1",
    "data/figure_3/searchandrescue/energy_log_20241203125834.pkl": "optimized_design_exp1",
    "data/figure_3/searchandrescue/energy_log_20241203130333.pkl": "optimized_design_exp1",
    "data/figure_3/searchandrescue/energy_log_20241203130719.pkl": "optimized_design_exp1",
    # "data/figure_3/searchandrescue/energy_log_20241203163525.pkl": "searchrescue",
    # "data/figure_3/searchandrescue/energy_log_20241203163828.pkl": "searchrescue",
    "data/figure_3/searchandrescue/energy_log_20241203173752.pkl": "optimized_design_exp2",
    "data/figure_3/searchandrescue/energy_log_20241203174155.pkl": "optimized_design_exp2",
    "data/figure_3/searchandrescue/energy_log_20241203174514.pkl": "optimized_design_exp2",
    "data/figure_3/searchandrescue/energy_log_20241203174830.pkl": "optimized_design_exp2",
    # Add more mappings as needed for other files
}

# =======================
# Data Extraction and Processing
# =======================

for file_idx, file_path in enumerate(file_paths):
    try:
        with open(file_path, "rb") as file:
            data = pickle.load(file)
    except FileNotFoundError:
        print(f"File {file_path} not found. Skipping.")
        continue
    except Exception as e:
        print(f"Error loading {file_path}: {e}. Skipping.")
        continue

    # Flatten the data: convert batches into a single sorted list of entries
    flattened_data = []
    for batch in data:
        if isinstance(batch, list):
            for entry in batch:
                flattened_data.append(entry)

    # Sort the flattened data by timestamp
    flattened_data.sort(key=lambda x: x.get("timestamp", 0))

    # Initialize list to store runs for this file
    runs = []

    # Parameters for run detection
    required_command = [0, -0.35]  # We only check the first two elements
    look_ahead_duration = 0  # seconds
    run_duration = 120  # seconds after run start
    last_run_end_time = -np.inf  # To avoid overlapping runs

    # Extract timestamps for efficient searching
    timestamps = [entry.get("timestamp", 0) for entry in flattened_data]
    total_entries = len(flattened_data)

    for current_idx, entry in enumerate(flattened_data):
        command = entry.get("command", [])
        timestamp = entry.get("timestamp", 0)

        # Skip if within an ongoing run
        if timestamp < last_run_end_time:
            continue

        # Check if the command matches [0, -0.35, X]
        if (
            len(command) >= 2
            and command[0] == required_command[0]
            and round(command[1], 4) == required_command[1]
        ):
            # Define the target timestamp to look ahead
            target_timestamp = timestamp + look_ahead_duration

            # Find the index where timestamp >= target_timestamp
            target_idx = bisect.bisect_left(
                timestamps, target_timestamp, current_idx + 1
            )

            if target_idx < total_entries:
                target_entry = flattened_data[target_idx]
                target_command = target_entry.get("command", [])

                # Check if the command at target_timestamp still matches [0, -0.35, X]
                if (
                    len(target_command) >= 2
                    and target_command[0] == required_command[0]
                    and round(target_command[1], 4) == required_command[1]
                ):
                    # Valid run detected
                    run_start_time = timestamp
                    run_end_time = run_start_time + run_duration

                    # Collect all entries within the run duration
                    # Find the index where timestamp >= run_end_time
                    end_idx = bisect.bisect_left(
                        timestamps, run_end_time, target_idx + 1
                    )

                    run_entries = flattened_data[current_idx:end_idx]

                    if not run_entries:
                        print(
                            f"No data entries found for the run starting at {run_start_time} in file {file_path}. Skipping this run."
                        )
                        continue

                    # Initialize run data
                    current_run = {
                        "start_timestamp": run_start_time,
                        "end_timestamp": run_end_time,
                        "selected_timestamps": [],
                        "selected_energy_values": [],
                        "selected_forward_velocity": [],
                        "selected_motor_efforts": [],
                        "selected_motor_velocities": [],
                    }

                    # Populate run data
                    for run_entry in run_entries:
                        run_timestamp = run_entry.get("timestamp", 0)
                        run_command = run_entry.get("command", [])
                        energy = run_entry.get("energy")
                        motor_efforts = run_entry.get("motor_efforts", [0] * 12)
                        motor_velocities = run_entry.get("motor_velocities", [0] * 12)

                        # Validate energy
                        if energy is None:
                            print(
                                f"Warning: 'energy' is None at timestamp {run_timestamp} in file {file_path}. Skipping this entry."
                            )
                            continue

                        # Validate motor efforts and velocities
                        if len(motor_efforts) != 12:
                            print(
                                f"Warning: 'motor_efforts' does not have 12 values at timestamp {run_timestamp} in file {file_path}. Filling with zeros."
                            )
                            motor_efforts = [0] * 12
                        if len(motor_velocities) != 12:
                            print(
                                f"Warning: 'motor_velocities' does not have 12 values at timestamp {run_timestamp} in file {file_path}. Filling with zeros."
                            )
                            motor_velocities = [0] * 12

                        # Append data
                        current_run["selected_timestamps"].append(run_timestamp)
                        current_run["selected_energy_values"].append(energy)
                        current_run["selected_forward_velocity"].append(
                            run_command[1] if len(run_command) > 1 else 0
                        )
                        current_run["selected_motor_efforts"].append(motor_efforts)
                        current_run["selected_motor_velocities"].append(
                            motor_velocities
                        )

                    # Add the run to the list of runs
                    runs.append(current_run)

                    # Update last_run_end_time to prevent overlapping runs
                    last_run_end_time = run_end_time

    # After processing all runs for the file
    if not runs:
        print(f"No valid runs found in {file_path}. Skipping this file.")
        continue

    print(f"Amount of runs: {len(runs)} for file: {file_path}")

    # =======================
    # Process Each Run
    # =======================

    for run_idx, run in enumerate(runs):
        selected_timestamps = run["selected_timestamps"]
        selected_energy_values = run["selected_energy_values"]
        selected_forward_velocity = run["selected_forward_velocity"]
        selected_motor_efforts = run["selected_motor_efforts"]
        selected_motor_velocities = run["selected_motor_velocities"]

        # Ensure there is data to process
        if not selected_timestamps:
            print(
                f"No data to process for run {run_idx + 1} in file {file_path}. Skipping this run."
            )
            continue

        # Convert selected timestamps to a relative scale
        relative_time_selected = [
            t - selected_timestamps[0] for t in selected_timestamps
        ]

        # Adjust energy values to start at zero
        initial_energy = selected_energy_values[0]
        relative_energy_values = [e - initial_energy for e in selected_energy_values]

        # Retrieve the manually measured distance for this run
        distance_walked = distances[file_idx]  # in meters

        # Avoid division by zero for distance
        if distance_walked == 0:
            print(
                f"Warning: Distance walked is zero for run {run_idx + 1} in file {file_path}. Cannot compute CoT. Skipping this run."
            )
            continue

        # Calculate energy consumption per interval by dividing the data into equal parts
        points_per_interval = len(relative_time_selected) // num_intervals
        energy_consumed_per_run = relative_energy_values[-1] - relative_energy_values[0]

        # Convert motor efforts and velocities to NumPy arrays for efficient computation
        motor_efforts_np = np.array(selected_motor_efforts)  # Shape: (num_points, 12)
        motor_velocities_np = np.array(
            selected_motor_velocities
        )  # Shape: (num_points, 12)

        # =======================
        # Calculate Metric Power and Energy
        # =======================

        # Compute metric_power at each timestep
        # metric_power = heatloss_constant * sum(torque_i^2) + mechanical_power_constant * sum(torque_i * velocity_i) + power_system
        sum_square_torques = np.sum(
            np.square(motor_efforts_np), axis=1
        )  # Shape: (num_points,)
        sum_torque_vel = np.sum(
            motor_efforts_np * motor_velocities_np, axis=1
        )  # Shape: (num_points,)
        metric_power = (
            (heatloss_constant * sum_square_torques)
            + (mechanical_power_constant * sum_torque_vel)
            + power_system
        )  # Shape: (num_points,)

        metric_energy_per_timestep = np.cumsum(metric_power) * dt / 3600  # Energy in Wh

        # Calculate metric_energy by integrating metric_power over time
        metric_energy = np.sum(metric_power) * dt  # Energy in Watt-seconds (Joules)

        # Convert metric_energy to Whs (Watt-hours) if metric_power is in Watts and dt in seconds
        metric_energy_wh = metric_energy / 3600  # 1 Wh = 3600 J

        # =======================
        # Calculate CoT (Cost of Transport)
        # =======================

        cot_wh_per_m = energy_consumed_per_run / distance_walked  # Wh/m

        # Convert CoT to J/m for consistency with desired output
        cot_j_per_m = cot_wh_per_m * 3600  # 1 Wh = 3600 J

        metric_cot_wh_per_m = metric_energy_wh / distance_walked  # Metric CoT in Wh/m

        # Store the processed run data, including the manually measured distance and CoT
        processed_run = {
            "relative_time": relative_time_selected,
            "relative_energy": relative_energy_values,
            "forward_velocity": selected_forward_velocity,
            "motor_efforts": selected_motor_efforts,
            "motor_velocities": selected_motor_velocities,
            "energy_consumed_per_run": energy_consumed_per_run,
            "metric_power": metric_power,  # NumPy array
            "metric_energy_wh": metric_energy_wh,  # Total metric_energy in Wh
            "metric_energy_per_timestep": metric_energy_per_timestep,  # NumPy array
            "distance_walked": distance_walked,  # Manually measured distance in meters
            "cot_wh_per_m": cot_wh_per_m,  # Cost of Transport in Wh/m
            "metric_cot_wh_per_m": metric_cot_wh_per_m,  # Metric Cost of Transport in Wh/m
            "cot_j_per_m": cot_j_per_m,  # Cost of Transport in J/m
        }
        runs[run_idx] = processed_run

    # Append all runs from this file to the global list with file index
    all_runs.append({"file_idx": file_idx, "runs": runs})

# =======================
# Collect Metrics and Organize Results
# =======================

# Initialize the results dictionary
results_dict = {}

for file_runs in all_runs:
    file_idx = file_runs["file_idx"]
    runs = file_runs["runs"]
    file_basename = os.path.basename(file_paths[file_idx])

    # Retrieve the design name from the mapping
    design_name = design_names_mapping.get(file_basename, "unknown_design")

    # Collect CoT values in J/m
    cot_values_j_m = [run["cot_j_per_m"] for run in runs]

    # Collect raw energy and distances
    raw_energy = [run["energy_consumed_per_run"] for run in runs]
    raw_distances = [run["distance_walked"] for run in runs]

    # Organize the data into the desired format
    if design_name not in results_dict:
        results_dict[design_name] = {
            "raw": {
                "energy": raw_energy,
                "distances": raw_distances,
                "cot_j_per_m": cot_values_j_m,
            }
        }
    else:
        # If the design already exists, append the new runs
        results_dict[design_name]["raw"]["energy"].extend(raw_energy)
        results_dict[design_name]["raw"]["distances"].extend(raw_distances)
        results_dict[design_name]["raw"]["cot_j_per_m"].extend(cot_values_j_m)

# =======================
# Calculate Average and Standard Deviation for Each Design
# =======================

for design, metrics in results_dict.items():
    cot_values = metrics["raw"]["cot_j_per_m"]
    if len(cot_values) == 0:
        print(
            f"No CoT data available for design {design}. Skipping statistics calculation."
        )
        continue
    average_cot = np.mean(cot_values)
    std_cot = np.std(cot_values)
    results_dict[design]["average_cot_j_m"] = average_cot
    results_dict[design]["std_cot_j_m"] = std_cot

# =======================
# Print Scores and Relative Differences
# =======================

print("\n=== Scores per Design ===")
for design, metrics in results_dict.items():
    print(f"\nDesign: {design}")
    distances_list = []
    adjusted_energy_list = []
    adjusted_cot_list = []
    for run_num, (energy, distance, cot) in enumerate(
        zip(
            metrics["raw"]["energy"],
            metrics["raw"]["distances"],
            metrics["raw"]["cot_j_per_m"],
        ),
        start=1,
    ):
        print(
            f"  Run {run_num}: Energy Consumed = {energy:.6f} Wh, Distance Walked = {distance:.2f} meters, CoT = {cot:.4f} J/m"
        )

        energy_adjusted = energy - system_energy
        cot_adjusted = energy_adjusted / distance * 3600

        distances_list.append(distance)
        adjusted_energy_list.append(energy_adjusted)
        adjusted_cot_list.append(cot_adjusted)

        print(
            f"  Run {run_num}: Energy Consumed Adjusted = {energy_adjusted:.6f} Wh, Distance Walked = {distance:.2f} meters, CoT Adjusted = {cot_adjusted:.4f} J/m"
        )
    if "average_cot_j_m" in metrics and "std_cot_j_m" in metrics:
        print(f" Average Distance: {np.mean(distances_list):.2f} meters")
        print(
            f" Average Energy Consumed Adjusted: {np.mean(metrics['raw']['energy']):.6f} Wh"
        )
        print(f"  Average CoT: {metrics['average_cot_j_m']:.4f} J/m")
        print(f"  CoT Std Dev: {metrics['std_cot_j_m']:.4f} J/m")
        print(
            f"  Average Energy Consumed Adjusted: {np.mean(adjusted_energy_list):.6f} Wh"
        )
        print(f"  Average CoT Adjusted: {np.mean(adjusted_cot_list):.4f} J/m")
    else:
        print("  Average CoT and Std Dev not available.")

# =======================
# Save the Results Dictionary as a Pickle File
# =======================

# Define the output file path
output_file_path = "data/figure_3/rw_data/rw_data_policy4.pkl"

# Save as Pickle
try:
    with open(output_file_path, "wb") as pkl_file:
        pickle.dump(results_dict, pkl_file)
    print(f"\nResults have been saved to {output_file_path}")
except Exception as e:
    print(f"Error saving results to pickle file: {e}")

# =======================
# Optional: Verify the Saved Pickle File
# =======================

# Uncomment the following lines to verify the saved data
with open(output_file_path, "rb") as pkl_file:
    loaded_results = pickle.load(pkl_file)
    print("\nLoaded Results:")
    print(loaded_results)
