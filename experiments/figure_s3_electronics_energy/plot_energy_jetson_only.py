import sys
import os
import numpy as np
import matplotlib.pyplot as plt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from utils.data import load_pickle
from utils.plot.plot_utils import save_plot

# =======================
# Configuration
# =======================

# Path to the pickle file you want to visualize
file_path = "data/figure_s3/energy_log_20240926142051.pkl"  # Power usage Jetson no walking full loop running

# =======================
# Data Extraction and Processing
# =======================

# Replace pickle loading with load_pickle
try:
    data = load_pickle(file_path)
    if data is None:
        print(f"File {file_path} not found.")
        exit()
except Exception as e:
    print(f"Error loading {file_path}: {e}")
    exit()

# Initialize lists to store data
timestamps = []
energy_values = []

for batch in data:
    if not isinstance(batch, list):
        continue
    for entry in batch:
        timestamp = entry.get("timestamp", 0)
        energy = entry.get("energy")
        if energy is None:
            continue  # Skip entries without energy data
        timestamps.append(timestamp)
        energy_values.append(energy)

if len(energy_values) == 0:
    print("No energy data found.")
    exit()

# Convert timestamps to relative times, starting from zero
relative_time = np.array(timestamps) - timestamps[0]

# Check the last relative timestamp and print it
last_relative_timestamp = relative_time[-1]
print(f"Last relative timestamp: {last_relative_timestamp}")

# Adjust energy values to start from zero
initial_energy = energy_values[0]
relative_energy = np.array(energy_values) - initial_energy

# Filter data to include only up to 480 seconds
max_time = 480
filtered_indices = relative_time <= max_time
relative_time = relative_time[filtered_indices]
relative_energy = relative_energy[filtered_indices]

# =======================
# Plot Measured Energy Consumption Over Time
# =======================

# Create the figure and axis

textwidth = 7.1413 * 0.495  # Match the \textwidth in inches
aspect_ratio = 0.618  # Golden ratio for pleasing plots
figsize = (textwidth, textwidth * aspect_ratio)

fig, ax = plt.subplots(figsize=figsize)  # Match aspect ratio of second script

# Plot the data with improved styling
ax.plot(
    relative_time,
    relative_energy,
    label=r"Measured Energy Consumption",
    color="black",
    linewidth=2,
)

# Set the title and labels
ax.set_xlabel(r"Time (s)")
ax.set_ylabel(r"Energy Consumed (Wh)")

# Set x and y limits to start from zero
ax.set_xlim(left=0, right=510)  # Add a bit of space to the right of the last number
ax.set_ylim(bottom=0)

# Customize grid and spines
ax.grid(True, linestyle="--", alpha=0.5)

# Remove the top and right spines
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

# Adjust layout for better spacing
plt.tight_layout()

# Save and display the plot
plot_path = f"plots/figure_s3/energy_jetson_only.pdf"
save_plot(fig, plot_path)
