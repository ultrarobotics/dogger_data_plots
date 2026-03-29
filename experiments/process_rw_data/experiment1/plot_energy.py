import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.gridspec import GridSpec
import bisect
import sys

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
    # "data/energy_log_20240913154013.pkl",  # nominal no pea
    # ... (other file paths)
    "data/figure_3/inspection/energy_log_20240930102638.pkl",  # NP nominal no pea 1 1 1 0 0
    "data/figure_3/inspection/energy_log_20240930124136.pkl",  # NP nominal with pea 1 1 1 0.025 0.005
    "data/figure_3/inspection/energy_log_20240930175939.pkl",  # NP optimized with pea 0.78 1.0 1.3 0.033 0.006
    "data/figure_3/inspection/energy_log_20241203182400.pkl",  # searchrescue
]

# Define colors using the viridis colormap
radar_colors = plt.cm.viridis(
    np.linspace(0, 1, len(file_paths))
)  # Generates a list of RGBA tuples

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
manual_distances = {
    "energy_log_20240930102638.pkl": [0, 29.82, 30.12, 30.22, 29.92],
    "energy_log_20240930124136.pkl": [31.64, 31.49, 31.97, 31.97],
    "energy_log_20240930175939.pkl": [32.47, 33.59, 33.47, 34.27],
    "energy_log_20241203182400.pkl": [29.72, 30.12, 30.02, 30.22],
    # Add more entries as needed for other files
    # "energy_log_filename.pkl": [distance_run1, distance_run2, distance_run3, distance_run4],
}

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
        print(f"File {file_path} not found. Skipping.", file=sys.stderr)
        continue
    except Exception as e:
        print(f"Error loading {file_path}: {e}. Skipping.", file=sys.stderr)
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
    required_command = [0, -0.5]  # We only check the first two elements
    look_ahead_duration = 29  # seconds
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

        # Check if the command matches [0, -0.5, X]
        if len(command) >= 2 and command[:2] == required_command:
            # Define the target timestamp to look ahead
            target_timestamp = timestamp + look_ahead_duration

            # Find the index where timestamp >= target_timestamp
            target_idx = bisect.bisect_left(
                timestamps, target_timestamp, current_idx + 1
            )

            if target_idx < total_entries:
                target_entry = flattened_data[target_idx]
                target_command = target_entry.get("command", [])

                # Check if the command at target_timestamp still matches [0, -0.5, X]
                if len(target_command) >= 2 and target_command[:2] == required_command:
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
                            f"No data entries found for the run starting at {run_start_time} in file {file_path}. Skipping this run.",
                            file=sys.stderr,
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
                                f"Warning: 'energy' is None at timestamp {run_timestamp} in file {file_path}. Skipping this entry.",
                                file=sys.stderr,
                            )
                            continue

                        # Validate motor efforts and velocities
                        if len(motor_efforts) != 12:
                            print(
                                f"Warning: 'motor_efforts' does not have 12 values at timestamp {run_timestamp} in file {file_path}. Filling with zeros.",
                                file=sys.stderr,
                            )
                            motor_efforts = [0] * 12
                        if len(motor_velocities) != 12:
                            print(
                                f"Warning: 'motor_velocities' does not have 12 values at timestamp {run_timestamp} in file {file_path}. Filling with zeros.",
                                file=sys.stderr,
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
        print(
            f"No valid runs found in {file_path}. Skipping this file.", file=sys.stderr
        )
        continue

    print(f"Amount of runs: {len(runs)} for file: {file_path}")

    # Retrieve the manually measured distances for the current file
    current_file_basename = os.path.basename(file_path)
    distances = manual_distances.get(current_file_basename, [])

    if not distances:
        print(
            f"No manual distances provided for {current_file_basename}. Please add them to the 'manual_distances' dictionary.",
            file=sys.stderr,
        )
        # Optionally, you can skip processing this file or handle it differently
        continue

    # Check if the number of distances matches the number of runs
    if len(distances) != len(runs):
        print(
            f"Number of manual distances ({len(distances)}) does not match number of runs ({len(runs)}) for file {current_file_basename}. Please verify.",
            file=sys.stderr,
        )
        # Optionally, you can skip processing this file or handle it differently
        continue

    # =======================
    # Skip First Run for Specific Files
    # =======================

    if current_file_basename in files_to_skip_first_run:
        if len(runs) > 0:
            print(
                f"Discarding the first run for {current_file_basename} as per configuration.",
                file=sys.stderr,
            )
            # Remove the first run
            runs = runs[1:]
            # Also remove the first distance
            distances = distances[1:]
            manual_distances[current_file_basename] = distances
            # Update the runs in all_runs (to be appended below)
        else:
            print(f"No runs to discard for {current_file_basename}.", file=sys.stderr)

    # Re-check the number of distances after discarding
    if current_file_basename in files_to_skip_first_run:
        if len(distances) != len(runs):
            print(
                f"After discarding, number of manual distances ({len(distances)}) does not match number of runs ({len(runs)}) for file {current_file_basename}. Please verify.",
                file=sys.stderr,
            )
            continue

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

# Save the cumulative energy plot
cumulative_plot_path = "utils/energy_exp1.pdf"
os.makedirs(os.path.dirname(cumulative_plot_path), exist_ok=True)
plt.savefig(cumulative_plot_path, dpi=300, bbox_inches="tight")
print(f"Cumulative energy consumption plot saved to {cumulative_plot_path}")
