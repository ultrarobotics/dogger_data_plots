import os
import sys
import re
import numpy as np
import matplotlib.pyplot as plt

# Ensure parent directory is in sys.path for utility imports
script_dir = os.path.dirname(__file__)
parent_dir = os.path.abspath(os.path.join(script_dir, "../.."))
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from utils.data import load_pickle
from utils.plot.plot_utils import save_plot
from utils.plot.plotting_utils import create_bar_chart


def load_nominal_vs_optimized_results(results_dir):
    """
    Load results from nominal_vs_optimized.

    Args:
        results_dir (str): Directory containing the .pkl result files.

    Returns:
        dict: Nested dictionary containing nominal and optimized designs per policy.
              Each design contains 'design', 'score' (average), and 'score_std' (std deviation).
    """
    results = {}
    for filename in os.listdir(results_dir):
        if filename.endswith(".pkl") and not filename.startswith("cot_statistics"):
            filepath = os.path.join(results_dir, filename)
            print(f"Loading {filepath}...")
            data = load_pickle(filepath)
            results.update(data)
    return results


def load_cot_statistics(filepath):
    """
    Load 'cot_statistics_policyX.pkl' which contains average and std of cot_j_m, as well as raw energy and distances.

    Args:
        filepath (str): Path to the 'cot_statistics_policyX.pkl' file.

    Returns:
        dict: Data from cot_statistics_policyX.pkl including average_cot_j_m, std_cot_j_m, and raw energy/distances.
    """
    cot_stats = load_pickle(filepath)
    return cot_stats


def extract_design(design, param_keys):
    """
    Extract parameter values from a design, handling both list and dict structures.

    Args:
        design (list or dict): The design data.
        param_keys (list of str): Parameter keys to extract.

    Returns:
        list: List of parameter values in the order of param_keys.
    """
    if isinstance(design, list):
        # Assume the list order matches param_keys
        if len(design) != len(param_keys):
            raise ValueError("Design list length does not match parameter keys length.")
        return design
    elif isinstance(design, dict):
        # Extract values based on param_keys
        try:
            return [design[key] for key in param_keys]
        except KeyError as e:
            raise KeyError(f"Missing key {e} in design dictionary.")
    else:
        raise TypeError("Design must be either a list or a dict.")


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


def calculate_adjusted_cotr(raw_energy, motor_power=16.2, run_time=120, distances=None):
    """
    Calculate the adjusted CoTr by subtracting the motor energy from the raw energy and dividing by distances.

    Args:
        raw_energy (list of float): Raw energy values (in Wh) from the dictionary.
        motor_power (float): Motor power in watts (default is 16.2 W).
        run_time (float): Run time in seconds (default is 120 seconds).
        distances (list of float): Measured distances corresponding to each energy value.

    Returns:
        list of float: Adjusted CoTr values for each trial.
    """
    if distances is None:
        distances = [1.0] * len(raw_energy)  # Default to avoid division by zero
    # Convert motor energy usage to watt-hours
    energy_used_wh = (motor_power * run_time) / 3600  # Convert motor energy to Wh
    print(f"System energy used: {energy_used_wh:.4f} Wh")
    # Subtract motor energy from raw energy and calculate adjusted CoTr
    adjusted_cotr = []
    for energy, dist in zip(raw_energy, distances):
        if dist != 0:
            adjusted = (energy - energy_used_wh) / dist
        else:
            adjusted = 0.0  # Avoid division by zero
            print(f"Warning: Distance is zero, setting adjusted CoTr to 0.0")
        adjusted_cotr.append(adjusted)
    print(f"Adjusted energy values: {adjusted_cotr}")
    return adjusted_cotr


def plot_relative_nominal_vs_optimized(
    policy_key,
    data,
    param_keys,
    scaling_factors,
    real_world_scores=None,
    real_world_stds=None,
    output_dir=None,
):
    """
    Plot a relative bar chart comparing each design to Nominal Design 1 for both
    simulation and real-world results. Scores are expressed as percentage differences.
    Nominal Design 1 is excluded from the plot.

    Args:
        policy_key (str): The policy identifier.
        data (dict): Design data for the policy.
        param_keys (list of str): Parameter keys.
        scaling_factors (list of float): Scaling factors for parameters.
        real_world_scores (list of float): Real-world average scores.
        real_world_stds (list of float): Real-world score standard deviations.
        output_dir (str): Directory to save the plots.
    """
    try:
        # Extract nominal designs and their scores
        nominal_designs = []
        nominal_scores = []
        nominal_stds = []
        for i in [1, 2]:
            key = f"nominal_design_{i}"
            if key in data:
                design = data[key]["design"]
                score = data[key]["score"]
                std = data[key]["score_std"]
                nominal_designs.append(design)
                nominal_scores.append(score)
                nominal_stds.append(std)
            else:
                print(
                    f"Warning: '{key}' not found in data for policy '{policy_key}'. Substituting defaults."
                )
                nominal_designs.append([1.0] * len(param_keys))  # Default design
                nominal_scores.append(0.0)
                nominal_stds.append(0.0)

        # Extract optimized designs
        optimized_designs = []
        optimized_scores = []
        optimized_stds = []
        optimized_pattern = re.compile(r"optimized_design_exp\d+")
        for key in data:
            if optimized_pattern.fullmatch(key):
                design = data[key]["design"]
                score = data[key]["score"]
                std = data[key]["score_std"]
                optimized_designs.append(design)
                optimized_scores.append(score)
                optimized_stds.append(std)

        if not optimized_designs:
            print(
                f"Warning: No optimized designs found for policy '{policy_key}'. Skipping plot."
            )
            return
    except (KeyError, TypeError, ValueError) as e:
        print(
            f"Error extracting designs or scores: {e}. Skipping plot for {policy_key}."
        )
        return

    # Combine simulation scores and stds (excluding Nominal Design 1)
    if len(nominal_scores) < 1:
        print(
            f"Error: Not enough nominal scores for policy '{policy_key}'. Skipping plot."
        )
        return

    simulation_scores = (
        nominal_scores[1:] + optimized_scores
    )  # Exclude Nominal Design 1
    simulation_stds = nominal_stds[1:] + optimized_stds  # Exclude Nominal Design 1

    # Combine real-world scores and stds (excluding Nominal Design 1)
    if real_world_scores is not None and real_world_stds is not None:
        if len(real_world_scores) < 1:
            print(
                f"Warning: Real-world scores for policy '{policy_key}' are insufficient. Substituting zeros."
            )
            real_world_scores_list = [0.0] * len(simulation_scores)
            real_world_stds_list = [0.0] * len(simulation_scores)
        else:
            real_world_scores_list = [
                score if score is not None else 0.0 for score in real_world_scores
            ]
            real_world_stds_list = [
                std if std is not None else 0.0 for std in real_world_stds
            ]
            # Exclude Nominal Design 1 from real-world data
            real_world_scores_list = real_world_scores_list[1:]
            real_world_stds_list = real_world_stds_list[1:]
    else:
        # If no real-world data, substitute zeros
        real_world_scores_list = [0.0] * len(simulation_scores)
        real_world_stds_list = [0.0] * len(simulation_scores)

    # Identify the baseline (Nominal Design 1)
    nominal_1_sim = nominal_scores[0] if len(nominal_scores) > 0 else 0.0
    nominal_1_real = (
        real_world_scores[0]
        if (real_world_scores and len(real_world_scores) > 0)
        else 0.0
    )

    # Compute relative differences in percentage
    def relative_diff(value, baseline):
        if baseline == 0.0:
            # Cannot compute relative difference
            return 0.0
        else:
            return (value / baseline - 1.0) * 100.0

    def relative_diff_std(value, value_std, baseline, baseline_std):
        if baseline == 0.0 or value == 0.0:
            return 0.0
        else:
            rel = value / baseline
            # Propagate uncertainty
            rel_std = (
                rel
                * np.sqrt((value_std / value) ** 2 + (baseline_std / baseline) ** 2)
                * 100.0
            )
            return rel_std

    relative_sim_scores = []
    relative_sim_stds = []
    relative_real_scores = []
    relative_real_stds = []

    for i, (sim_score, sim_std, real_score, real_std) in enumerate(
        zip(
            simulation_scores,
            simulation_stds,
            real_world_scores_list,
            real_world_stds_list,
        )
    ):
        rel_sim = relative_diff(sim_score, nominal_1_sim)
        rel_sim_std = relative_diff_std(
            sim_score,
            sim_std,
            nominal_1_sim,
            nominal_stds[0] if len(nominal_stds) > 0 else 0.0,
        )
        relative_sim_scores.append(rel_sim)
        relative_sim_stds.append(rel_sim_std)

        rel_real = relative_diff(real_score, nominal_1_real)
        rel_real_std = relative_diff_std(
            real_score,
            real_std,
            nominal_1_real,
            real_world_stds_list[0] if len(real_world_stds_list) > 0 else 0.0,
        )
        relative_real_scores.append(rel_real)
        relative_real_stds.append(rel_real_std)

    # Define design labels (excluding Nominal Design 1)
    design_labels_combined = [r"$d^n_2$", r"$d^*_1$", r"$d^*_2$"]

    # Debug: Print the energy and distance data being used
    print(f"\nDebug Info for '{policy_key}':")
    print(f"Nominal Design 1 (Baseline) Simulation Score: {nominal_1_sim}")
    print(f"Nominal Design 1 (Baseline) Real-World Score: {nominal_1_real}")
    print(f"Simulation Scores (excluding Nominal Design 1): {simulation_scores}")
    print(f"Real-World Scores (excluding Nominal Design 1): {real_world_scores_list}")
    print(f"Relative Simulation Scores: {relative_sim_scores}")
    print(f"Relative Real-World Scores: {relative_real_scores}")

    # Print the relative differences for debugging
    print(f"\nRelative Differences for '{policy_key}':")
    for name, sim_val, sim_err, rw_val, rw_err in zip(
        design_labels_combined,
        relative_sim_scores,
        relative_sim_stds,
        relative_real_scores,
        relative_real_stds,
    ):
        print(
            f"  {name}: Simulation: {sim_val:.2f}% ± {sim_err:.2f}%, Real-World: {rw_val:.2f}% ± {rw_err:.2f}%"
        )

    # Prepare data for plotting
    bar_scores_list = [relative_sim_scores, relative_real_scores]
    bar_errors_list = [relative_sim_stds, relative_real_stds]
    group_labels = [
        r"{\fontfamily{ptm}\selectfont Simulation}",
        r"{\fontfamily{ptm}\selectfont Real-World}",
    ]

    # Generate colors
    num_designs = len(design_labels_combined)
    design_colors = plt.cm.viridis(np.linspace(0, 1, num_designs + 1)).tolist()[
        1:
    ]  # Exclude first color (baseline)

    # Define hatches
    hatches = ["", "///"]  # No hatch for simulation, and '///' for real-world

    textwidth = 7.1413 * 0.495  # Match the \textwidth in inches
    aspect_ratio = 0.618  # Golden ratio for pleasing plots
    figsize = (textwidth, textwidth * aspect_ratio)

    # Create bar chart
    try:
        fig_bar, ax_bar = plt.subplots(figsize=figsize)
        create_bar_chart(
            ax=ax_bar,
            bar_scores_list=bar_scores_list,  # Relative percentage differences
            bar_errors_list=bar_errors_list,
            bar_labels=design_labels_combined,
            design_colors=design_colors,
            hatches=hatches,
            xlabel=r"{\fontfamily{ptm}\selectfont Task 2: Relative} $CoT$ {\fontfamily{ptm}\selectfont change compared to} $d^n_1$ {\fontfamily{ptm}\selectfont[\%]}",
            group_labels=group_labels,
            invert_xaxis=True,
        )

        plt.tight_layout()

        # Save bar chart
        bar_output_path = os.path.join(output_dir, f"relative_bar_chart_{policy_key}.pdf")
        save_plot(fig_bar, bar_output_path)
        print(f"Relative bar chart saved to {bar_output_path}.")

    except Exception as e:
        print(f"Error plotting relative bar chart for '{policy_key}': {e}")


def main():
    results_dir = "data/figure_3/evaluated_designs"
    rw_data_dir = (
        "data/figure_3/rw_data"  # Directory containing cot_statistics_policyX.pkl files
    )
    results = load_nominal_vs_optimized_results(results_dir)
    print("Loaded Results:")
    print(results)

    if not results:
        print("No results loaded. Please check the results directory.")
        return

    # Define scaling factors to convert units (1 for [-], 1000 for [mm])
    scaling_factors = [1, 1, 1, 1000, 1000]

    # Define the order of parameter keys as they appear in the design dicts
    param_keys = [
        "scaling_thigh",
        "scaling_shank",
        "scaling_foot",
        "wheel_diameter",
        "offset_spring",
    ]

    # Define output directory if it doesn't exist
    output_dir = "plots/figure_3"  # You can change this if needed
    os.makedirs(output_dir, exist_ok=True)

    # Iterate over each policy and plot
    for policy_key, data in results.items():
        print(f"\nProcessing '{policy_key}'...")

        # Attempt to load cot_statistics for this policy
        cot_statistics_filename = f"rw_data_{policy_key}.pkl"
        cot_statistics_path = os.path.join(rw_data_dir, cot_statistics_filename)
        if os.path.exists(cot_statistics_path):
            try:
                cot_stats = load_cot_statistics(cot_statistics_path)
                print(
                    f"Loaded Real-World Scores and Std Deviations for '{policy_key}'."
                )
            except Exception as e:
                print(
                    f"Error loading '{cot_statistics_filename}': {e}. Substituting zeros for real-world data."
                )
                cot_stats = None
        else:
            print(
                f"'{cot_statistics_filename}' not found. Substituting zeros for real-world data."
            )
            cot_stats = None  # No real-world data available

        # Prepare real-world scores and stds
        real_world_scores = []
        real_world_stds = []

        if cot_stats:
            # Extract real-world averages and stds from cot_stats
            sorted_keys = sorted(cot_stats.keys())
            for key in sorted_keys:
                design_data = cot_stats[key]
                avg = design_data.get("average_cot_j_m", 0.0)
                std = design_data.get("std_cot_j_m", 0.0)
                real_world_scores.append(avg)
                real_world_stds.append(std)
        else:
            # No real-world data; will substitute zeros later
            pass

        # Determine the expected number of designs
        num_nominal = 2  # Assuming two nominal designs per policy
        num_optimized = len(
            [key for key in data if re.fullmatch(r"optimized_design_exp\d+", key)]
        )
        expected_designs = num_nominal + num_optimized

        if cot_stats:
            # Handle cases where cot_stats might have less data than required
            if len(real_world_scores) < expected_designs:
                missing = expected_designs - len(real_world_scores)
                print(
                    f"'{cot_statistics_filename}' is missing data for {missing} design(s). Substituting zeros."
                )
                real_world_scores.extend([0.0] * missing)
                real_world_stds.extend([0.0] * missing)
        else:
            # Ensure we have exactly expected_designs scores
            real_world_scores = [0.0] * expected_designs
            real_world_stds = [0.0] * expected_designs

        # If cot_stats exists and real_world_scores is still empty, substitute zeros
        if cot_stats and not real_world_scores:
            real_world_scores = [0.0] * expected_designs
            real_world_stds = [0.0] * expected_designs

        # If cot_stats exists but real_world_scores is shorter, extend with zeros
        elif cot_stats and len(real_world_scores) < expected_designs:
            missing = expected_designs - len(real_world_scores)
            real_world_scores.extend([0.0] * missing)
            real_world_stds.extend([0.0] * missing)

        # If cot_stats does not exist, ensure real_world_scores and real_world_stds have expected_designs length
        elif not cot_stats:
            real_world_scores = [0.0] * expected_designs
            real_world_stds = [0.0] * expected_designs

        # If cot_stats exists but real_world_scores is longer, trim the excess
        if cot_stats and len(real_world_scores) > expected_designs:
            real_world_scores = real_world_scores[:expected_designs]
            real_world_stds = real_world_stds[:expected_designs]

        # Construct output directory paths
        policy_output_dir = os.path.join(output_dir, policy_key)
        os.makedirs(policy_output_dir, exist_ok=True)

        # Plot relative bar chart
        plot_relative_nominal_vs_optimized(
            policy_key=policy_key,
            data=data,
            param_keys=param_keys,
            scaling_factors=scaling_factors,
            real_world_scores=real_world_scores,
            real_world_stds=real_world_stds,
            output_dir=policy_output_dir,
        )
        print(f"Completed plotting for '{policy_key}'.")


if __name__ == "__main__":
    main()
