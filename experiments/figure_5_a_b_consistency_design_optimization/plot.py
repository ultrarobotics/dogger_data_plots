import os
import sys
import numpy as np
import matplotlib.pyplot as plt

# Ensure parent directory is in sys.path for utility imports
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data import load_pickle
from utils.plot.plot_utils import save_plot
from utils.plot.plotting_utils import (
    create_bar_chart,
    create_radar_chart,
    normalize_designs,
    radar_factory,
)

# Define paths
file_path = "data/figure_5/evaluated_designs"
output_dir = "plots/figure_5"

# Policies to analyze
plot_policies = [1, 4]


# Function to calculate percentage difference
def calculate_percent_diff(main_score, subdesign_scores):
    return [
        (subdesign - main_score) / main_score * 100 for subdesign in subdesign_scores
    ]


# Function to calculate the propagated standard deviation for percentage differences
def calculate_percent_diff_std(main_score, main_std, subdesign_scores, subdesign_stds):
    percent_diff_stds = []
    for score, std in zip(subdesign_scores, subdesign_stds):
        if main_score == 0.0 or score == 0.0:
            percent_diff_stds.append(0.0)
        else:
            # Calculate the ratio and then propagate the uncertainties
            ratio = score / main_score
            propagated_std = (
                ratio
                * np.sqrt((std / score) ** 2 + (main_std / main_score) ** 2)
                * 100.0
            )
            percent_diff_stds.append(propagated_std)
    return percent_diff_stds


# Process each policy
for policy in plot_policies:
    # Plot settings
    textwidth = 7.1413 * 0.495  # Match the \textwidth in inches
    aspect_ratio = 0.618  # Golden ratio for pleasing plots
    figsize = (textwidth, textwidth * aspect_ratio)

    data_path = os.path.join(file_path, f"evaluated_designs_policy{policy}.pkl")
    with open(data_path, "rb") as file:
        data = load_pickle(data_path)

    policy_key = f"policy{policy}"
    main_design_key = f"optimized_design_exp{policy}"
    if policy == 4:
        main_design_key = "optimized_design_exp2"
    subdesign_keys = [k for k in data[policy_key] if k != main_design_key]

    # Extract main score and subdesign scores
    main_score = data[policy_key][main_design_key]["score"]
    main_std = data[policy_key][main_design_key]["score_std"]
    subdesign_scores = [data[policy_key][k]["score"] for k in subdesign_keys]
    subdesign_stds = [data[policy_key][k]["score_std"] for k in subdesign_keys]
    subdesign_designs = [data[policy_key][k]["design"] for k in subdesign_keys]

    # Print main and subdesign scores
    print(f"Main design score for policy {policy}: {main_score}")
    for subdesign_key, subdesign_score in zip(subdesign_keys, subdesign_scores):
        print(f"Subdesign {subdesign_key} score: {subdesign_score}")

    # Calculate relative percentage differences and their standard deviations
    percent_diffs = calculate_percent_diff(main_score, subdesign_scores)
    percent_diff_stds = calculate_percent_diff_std(
        main_score, main_std, subdesign_scores, subdesign_stds
    )

    # Print calculated values
    print(f"Policy {policy}:")
    print(f"Main Score: {main_score}")
    print("Relative Percentage Differences (with stds):")
    for subdesign, diff, diff_std in zip(
        subdesign_keys, percent_diffs, percent_diff_stds
    ):
        print(f"  {subdesign}: {diff:.2f}% ± {diff_std:.2f}%")

    # Bar chart settings
    if policy == 1:
        design_labels_combined = [
            r"${d^{*,1}_{1}}$",
            r"${d^{*,2}_{1}}$",
            r"${d^{*,3}_{1}}$",
            r"${d^{*,4}_{1}}$",
            r"${d^{*,5}_{1}}$",
        ]
        xlabel = r"{\fontfamily{ptm}\selectfont Task 1: Relative} $CoT$ {\fontfamily{ptm}\selectfont change compared to} $d^*_1$ {\fontfamily{ptm}\selectfont[\%]}"
        design_colors = plt.cm.Paired(np.linspace(0, 1, 5)).tolist()
    elif policy == 4:
        design_labels_combined = [
            r"${d^{*,1}_{2}}$",
            r"${d^{*,2}_{2}}$",
            r"${d^{*,3}_{2}}$",
            r"${d^{*,4}_{2}}$",
            r"${d^{*,5}_{2}}$",
        ]
        xlabel = r"{\fontfamily{ptm}\selectfont Task 2: Relative} $CoT$ {\fontfamily{ptm}\selectfont change compared to} $d^*_2$ {\fontfamily{ptm}\selectfont[\%]}"
        design_colors = plt.cm.Paired(np.linspace(0, 1, 5)).tolist()

    # Bar chart data: use the calculated stds as error bars
    bar_scores_list = percent_diffs  # Relative percent differences for each subdesign
    bar_errors_list = percent_diff_stds

    # Plot bar chart using the utility
    try:
        fig_bar, ax_bar = plt.subplots(figsize=figsize)
        create_bar_chart(
            ax=ax_bar,
            bar_scores_list=[
                bar_scores_list
            ],  # Wrap in a list since it's a grouped bar chart
            bar_errors_list=[bar_errors_list],
            bar_labels=design_labels_combined,
            design_colors=design_colors,
            xlabel=xlabel,
            group_labels=None,  # No grouping labels in this case
        )
        ax_bar.axvline(
            x=0, color="black", linewidth=1, linestyle="-"
        )  # Highlight 0% difference
        plt.tight_layout()

        # Save plot
        bar_output_path = os.path.join(output_dir, f"consistency{policy}.pdf")
        save_plot(fig_bar, bar_output_path)
        plt.close(fig_bar)
        print(f"Relative bar chart saved to {bar_output_path}.")

    except Exception as e:
        print(f"Error plotting relative bar chart for policy {policy}: {e}")

    # Plot radar chart
    try:
        param_ranges = [
            (0.7, 1.3),  # Scale Thigh [-]
            (0.7, 1.3),  # Scale Shank [-]
            (0.7, 1.3),  # Scale Foot [-]
            (0.0, 50.0),  # Wheel Diameter [mm]
            (0.0, 10.0),  # Spring Offset [mm]
        ]

        scaling_factors = [1, 1, 1, 1000, 1000]

        subdesign_designs_scaled = [
            [val * scale for val, scale in zip(design, scaling_factors)]
            for design in subdesign_designs
        ]

        # Normalize designs
        normalized_designs = normalize_designs(subdesign_designs_scaled, param_ranges)

        # Define parameter labels
        param_labels = [
            r"$\lambda_{1}$ {\fontfamily{ptm}\selectfont[-]}",
            r"$\lambda_{2}$ {\fontfamily{ptm}\selectfont[-]}",
            r"$\lambda_{3}$ {\fontfamily{ptm}\selectfont[-]}",
            r"$\diameter$ {\fontfamily{ptm}\selectfont[mm]}",
            r"$o_s$ {\fontfamily{ptm}\selectfont[mm]}",
        ]

        # Plot settings for radar chart
        textwidth = 7.1413 * 0.495  # Match the \textwidth in inches
        aspect_ratio = 1.0
        figsize = (textwidth, textwidth * aspect_ratio)

        num_params = len(param_labels)
        theta = radar_factory(num_params)

        fig_radar, ax_radar = plt.subplots(
            figsize=figsize, subplot_kw=dict(projection="radar")
        )
        create_radar_chart(
            ax=ax_radar,
            theta=theta,
            designs=normalized_designs,
            colors=design_colors,
            design_labels=design_labels_combined,
            param_labels=param_labels,
            param_ranges=param_ranges,
        )

        radar_output_path = os.path.join(output_dir, f"radar_chart_{policy_key}.pdf")
        fig_radar.savefig(radar_output_path, dpi=300, bbox_inches="tight")
        plt.close(fig_radar)
        print(f"Radar chart saved to {radar_output_path}.")
    except Exception as e:
        print(f"Error plotting radar chart for policy {policy}: {e}")
