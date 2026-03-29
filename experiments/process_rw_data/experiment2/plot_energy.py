import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.gridspec import GridSpec
import bisect
import sys

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


# =======================
# Configuration
# =======================

# Enable LaTeX rendering for consistency
plt.rc("text", usetex=True)
plt.rc("font", family="serif", serif="Times", size=10)

# Include necessary packages in the LaTeX preamble
rcParams["text.latex.preamble"] = r"""
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{wasysym}
    \usepackage{mathptmx}  % Times font for math
"""

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
    # "data/figure_3/searchandrescue/energy_log_20241203163525.pkl", # searchrescue run1 without slight offset
    # "data/figure_3/searchandrescue/energy_log_20241203163828.pkl", # searchrescue run2 without slight offset
    "data/figure_3/searchandrescue/energy_log_20241203173752.pkl",  # searchrescue run3
    "data/figure_3/searchandrescue/energy_log_20241203174155.pkl",  # searchrescue run4
    "data/figure_3/searchandrescue/energy_log_20241203174514.pkl",  # searchrescue run5
    "data/figure_3/searchandrescue/energy_log_20241203174830.pkl",  # searchrescue run6
]

# Define a mapping from each pickle file's basename to a design name
design_names_mapping = {
    "energy_log_20241128111442.pkl": "nominal_design_1",
    "energy_log_20241128112136.pkl": "nominal_design_1",
    "energy_log_20241128112640.pkl": "nominal_design_1",
    "energy_log_20241128113009.pkl": "nominal_design_1",
    "energy_log_20241202113842.pkl": "nominal_design_2",
    "energy_log_20241202114456.pkl": "nominal_design_2",
    "energy_log_20241202114806.pkl": "nominal_design_2",
    "energy_log_20241202115126.pkl": "nominal_design_2",
    "energy_log_20241202172116.pkl": "optimized_design_exp1",
    "energy_log_20241203125834.pkl": "optimized_design_exp1",
    "energy_log_20241203130333.pkl": "optimized_design_exp1",
    "energy_log_20241203130719.pkl": "optimized_design_exp1",
    # "energy_log_20241203163525.pkl": "searchrescue",
    # "energy_log_20241203163828.pkl": "searchrescue",
    "energy_log_20241203173752.pkl": "optimized_design_exp2",
    "energy_log_20241203174155.pkl": "optimized_design_exp2",
    "energy_log_20241203174514.pkl": "optimized_design_exp2",
    "energy_log_20241203174830.pkl": "optimized_design_exp2",
    # Add more mappings as needed for other files
}

# Define colors using the viridis colormap
radar_colors = plt.cm.viridis(np.linspace(0, 1, 4))  # Generates a list of RGBA tuples

# Define labels for different files for better visualization
labels = [
    r"$\boldsymbol{d^n_1}$",
    r"$\boldsymbol{d^n_2}$",
    r"$\boldsymbol{d^*_1}$",
    r"$\boldsymbol{d^*_2}$",
]

# Initialize lists to store data from all files and all runs
all_runs = []  # Each element corresponds to a file and contains a list of runs

# Define motor indices to plot (0-based indexing)
motor_indices_to_plot = [2, 5, 8, 11]  # Motors 3, 6, 9, 12 if 1-based

num_intervals = 1

# =======================
# Define Constants for Metric Calculation
# =======================

# Define the heatloss and mechanical power constants
dt = 0.04  # seconds
heatloss_constant = 0.5299
mechanical_power_constant = 0.6091
power_system = 16.2  # system power consumption in Watts, experimentally validated

# =======================
# Manual Distance Input
# =======================

# Define a dictionary where each key is the basename of a pickle file,
# and the value is a list of distances walked (in meters) for each run in that file.
distance_file = ["data/figure_3/searchandrescue/distances/distances.pkl"]

# Load distances from pickle and sort them in the desired order
distances = load_pickle_file(distance_file[0])
if distances:
    distances = sort_distances_by_order(distances)
    print("Sorted distances:", distances)

# Convert to a list in the sorted order
distances = list(distances.values())
print("Distances list:", distances)

# =======================
# Define Files to Skip Runs
# =======================

# List of files for which the first run should be discarded
files_to_skip_first_run = [
    "energy_log_20240930102638.pkl",  # Add more filenames if needed
]

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
                f"No data to process for run {run_idx + 1} in file {file_path}. Skipping this run.",
                file=sys.stderr,
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
        distance_walked = distances[run_idx]  # in meters

        # Avoid division by zero for distance
        if distance_walked == 0:
            print(
                f"Warning: Distance walked is zero for run {run_idx + 1} in file {file_path}. Cannot compute CoT. Skipping this run.",
                file=sys.stderr,
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
        # metric_power = heatloss_constant * sum(torque_i^2) + mechanical_power_constant * sum(torque_i * velocity_i)
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
        metric_energy = (
            np.sum(metric_power) * dt
        )  # Energy in the same unit as metric_power * time (e.g., W * s = J)

        # Convert metric_energy to Whs (Watt-hours) if metric_power is in Watts and dt in seconds
        metric_energy_wh = metric_energy / 3600  # 1 Wh = 3600 J

        # =======================
        # Calculate CoT (Cost of Transport)
        # =======================

        cot_wh_per_m = energy_consumed_per_run / distance_walked  # Wh/m

        # Store the processed run data, including the manually measured distance and CoT
        processed_run = {
            "relative_time": relative_time_selected,
            "relative_energy": relative_energy_values,
            "forward_velocity": selected_forward_velocity,
            "motor_efforts": selected_motor_efforts,
            "motor_velocities": selected_motor_velocities,
            "energy_consumed_per_run": energy_consumed_per_run,
            "metric_power": metric_power,  # Per-timestep metric_power
            "metric_energy_wh": metric_energy_wh,  # Total metric_energy in Wh
            "metric_energy_per_timestep": metric_energy_per_timestep,  # Metric energy per timestep in Wh
            "distance_walked": distance_walked,  # Manually measured distance in meters
            "cot_wh_per_m": cot_wh_per_m,  # Cost of Transport in Wh/m
        }
        runs[run_idx] = processed_run

    # Append all runs from this file to the global list with file index and color
    all_runs.append({"file_idx": file_idx, "runs": runs})

# Check if any data was loaded
if not all_runs:
    print("No valid data loaded from the provided pickle files.", file=sys.stderr)
    exit()

# ————————————————
# Regroup runs by design name
# ————————————————

# Build a map from design_name → list of runs
design_runs_map = {}
for file_entry in all_runs:
    file_idx = file_entry["file_idx"]
    runs = file_entry["runs"]
    # get the basename of the pickle to look up the design
    basename = os.path.basename(file_paths[file_idx])
    design_name = design_names_mapping.get(basename, f"unknown_design_{file_idx}")
    design_runs_map.setdefault(design_name, []).extend(runs)

# Replace all_runs with a list keyed by design
file_idx = 0
all_runs_by_design = []
for design_name, runs in design_runs_map.items():

    all_runs_by_design.append(
        {
            "file_idx": file_idx,  # Keep the file index for reference
            "design_name": design_name,
            "runs": runs,
        }
    )

    file_idx = file_idx + 1

# Now overwrite all_runs for plotting
all_runs = all_runs_by_design

# Example: inspect grouping
for entry in all_runs:
    print(f"Design: {entry['design_name']} has {len(entry['runs'])} runs")

# =======================
# Plotting Section
# =======================

# Define a consistent color palette using viridis colormap
file_colors = radar_colors  # Already defined as viridis colormap

# -----------------------------------
# Plot 1: Cumulative Energy Consumption Over Time
# -----------------------------------

# Define figure size parameters
textwidth = 7.1413 * 1.0  # Match the \textwidth in inches
aspect_ratio = 0.425  # Golden ratio for pleasing plots
figsize_cumulative = (textwidth, textwidth * aspect_ratio)

# Create a figure for Cumulative Energy Consumption
fig_cumulative, ax_cumulative = plt.subplots(figsize=figsize_cumulative)

for file_runs in all_runs:
    file_idx = file_runs["file_idx"]
    runs = file_runs["runs"]
    file_path = file_paths[file_idx]
    file_basename = os.path.basename(file_path)
    label = labels[file_idx]
    color = file_colors[file_idx % len(file_colors)]

    cumulative_time = 0
    cumulative_energy = 0
    times = []
    energies = []

    for run in runs:
        rel_time = run["relative_time"]
        rel_energy = run["relative_energy"]

        # Adjust time and energy for cumulative plotting
        if times:
            # Offset time
            adjusted_time = [t + cumulative_time for t in rel_time]
            # Offset energy
            adjusted_energy = [e + cumulative_energy for e in rel_energy]
        else:
            adjusted_time = rel_time
            adjusted_energy = rel_energy

        times.extend(adjusted_time)
        energies.extend(adjusted_energy)

        # Update cumulative time and energy
        cumulative_time = adjusted_time[-1]
        cumulative_energy = adjusted_energy[-1]

    ax_cumulative.plot(
        times,
        energies,
        label=label,
        color=color,
        linewidth=2,
        linestyle="-",  # Solid lines
        alpha=0.9,
    )

# Customize the cumulative energy plot
ax_cumulative.set_xlabel(r"Time (s)")
ax_cumulative.set_ylabel(r"Energy Consumed (Wh)")

# Set x and y limits to start from zero and add some padding
ax_cumulative.set_xlim(left=0)
ax_cumulative.set_ylim(bottom=0)

# Customize grid and spines
ax_cumulative.grid(True, linestyle="--", alpha=0.5)
ax_cumulative.spines["top"].set_visible(False)
ax_cumulative.spines["right"].set_visible(False)

# Add legend with appropriate font size
ax_cumulative.legend()

# Adjust layout for better spacing
plt.tight_layout()

print(energies)

# Save the cumulative energy plot
cumulative_plot_path = "utils/energy_exp2.pdf"
os.makedirs(os.path.dirname(cumulative_plot_path), exist_ok=True)
plt.savefig(cumulative_plot_path, dpi=300, bbox_inches="tight")
print(f"Cumulative energy consumption plot saved to {cumulative_plot_path}")
