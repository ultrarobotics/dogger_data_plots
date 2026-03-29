#!/usr/bin/env python

import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Add parent directory to sys.path for utility imports
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data import load_pickle
from utils.plot.plot_utils import save_plot
from utils.plot.plotting_utils import create_distribution_plot

file_path = "data/figure_6/eval_metric_task_2.pkl"
data = load_pickle(file_path)

# Extract keys for universal and specialized designs, sorted by range index
univ_keys = sorted(
    [k for k in data if k.endswith("_universal")],
    key=lambda k: int(k.split("_range")[1].split("_")[0]),
)
spec_keys = sorted(
    [k for k in data if k.endswith("_specialized")],
    key=lambda k: int(k.split("_range")[1].split("_")[0]),
)

if len(univ_keys) != len(spec_keys):
    raise ValueError("The number of universal and specialized keys do not match.")

perc_diffs = []
design_list = []
for u_key, s_key in zip(univ_keys, spec_keys):
    universal_score = data[u_key]["score_mean"]
    specialized_score = data[s_key]["score_mean"]
    if data[u_key]["design"] != data[s_key]["design"]:
        raise ValueError(f"Designs do not match for keys {u_key} and {s_key}.")
    design = data[u_key]["design"]
    perc_diff = ((universal_score - specialized_score) / specialized_score) * 100
    if -75 <= perc_diff <= 75:
        design_list.append(design)
        perc_diffs.append(perc_diff)

# Labels and colors for fixed designs (first four)
fixed_labels = [r"${d^n_1}$", r"${d^n_2}$", r"${d^*_1}$", r"${d^*_2}$"]
num_fixed = 4
design_colors = plt.cm.viridis(np.linspace(0, 1, num_fixed)).tolist()

# Set up the figure
textwidth = 7.1413 * 0.5  # inches
aspect_ratio = 0.6
figsize = (textwidth, textwidth * aspect_ratio)
fig, ax = plt.subplots(figsize=figsize)

create_distribution_plot(
    ax,
    perc_diffs,
    fixed_labels,
    design_colors,
    xlabel=r"{$\pi_u$ {\fontfamily{ptm}\selectfont relative $CoT$ compared to} $\pi_s$ {\fontfamily{ptm}\selectfont[\%]}",
    kde=True,
)

plt.tight_layout()

# Print best and worst design indices
best_index = np.argmax(perc_diffs)
worst_index = np.argmin(perc_diffs)
print(f"Number of designs: {len(univ_keys)}")
print(f"Best design: {best_index}, Design: {design_list[best_index]}")
print(f"Worst design: {worst_index}, Design: {design_list[worst_index]}")

plot_path = os.path.join("plots/figure_6", "distribution_plot.pdf")
save_plot(fig, plot_path)
print(f"Distribution plot saved to {plot_path}")
