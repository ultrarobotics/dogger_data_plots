import numpy as np
import matplotlib.pyplot as plt
from matplotlib.projections.polar import PolarAxes
from matplotlib.projections import register_projection
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Patch

# Enable LaTeX rendering

plt.rcParams.update(
    {
        "text.usetex": True,
        "font.size": 10,
        "mathtext.fontset": "cm",
        "text.latex.preamble": r"""\usepackage{amsmath} \usepackage{amssymb} \usepackage{wasysym} """,
    }
)

# =====================================
# Radar Chart Utilities
# =====================================


def radar_factory(num_vars, frame="circle"):
    """
    Create a radar chart with `num_vars` axes.

    Args:
        num_vars (int): Number of variables (axes) for the radar chart.
        frame (str): Type of frame to use ('circle' or 'polygon').

    Returns:
        theta (np.ndarray): Angles for each axis.
    """
    theta = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)

    class RadarAxes(PolarAxes):
        name = "radar"

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.set_theta_zero_location("N")

        def fill(self, *args, closed=True, **kwargs):
            return super().fill(*args, closed=closed, **kwargs)

        def plot(self, *args, **kwargs):
            lines = super().plot(*args, **kwargs)
            for line in lines:
                self._close_line(line)

        def _close_line(self, line):
            x, y = line.get_data()
            if x[0] != x[-1]:
                x = np.concatenate((x, [x[0]]))
                y = np.concatenate((y, [y[0]]))
                line.set_data(x, y)

        def set_varlabels(self, labels):
            self.set_thetagrids(np.degrees(theta), labels)

    # Correctly register the RadarAxes projection
    register_projection(RadarAxes)
    return theta


def custom_tick_formatter(x, min_val, max_val):
    """
    Format tick labels by converting normalized values back to original scale.

    Args:
        x (float): Normalized value.
        min_val (float): Minimum original value.
        max_val (float): Maximum original value.

    Returns:
        str: Formatted tick label.
    """
    return f"{x * (max_val - min_val) + min_val:.2f}"


def normalize(value, min_val, max_val):
    """
    Normalize a value between min_val and max_val to a range of 0 to 1.

    Args:
        value (float): The value to normalize.
        min_val (float): Minimum value of the range.
        max_val (float): Maximum value of the range.

    Returns:
        float: Normalized value.
    """
    if max_val - min_val == 0:
        return 0.0  # Avoid division by zero
    return (value - min_val) / (max_val - min_val)


def normalize_designs(designs, ranges):
    """
    Normalize all designs based on the provided parameter ranges.

    Args:
        designs (list of list): List of designs, each design is a list of parameter values.
        ranges (list of tuple): List of (min, max) tuples for each parameter.

    Returns:
        list of list: Normalized designs.
    """
    return [
        [
            normalize(val, min_val, max_val)
            for val, (min_val, max_val) in zip(design, ranges)
        ]
        for design in designs
    ]


def create_radar_chart(
    ax, theta, designs, colors, design_labels, param_labels, param_ranges
):
    # Set up the radar chart
    ax.set_ylim(0, 1)
    ax.set_yticks([0.25, 0.5, 0.75, 1])
    ax.set_yticklabels([])  # Remove default radial labels
    ax.grid(True, color="gray", linestyle="--", linewidth=0.5, alpha=0.5)

    # Make the outer circle (spine) gray to match the grid lines
    ax.spines["polar"].set_color("gray")
    ax.spines["polar"].set_linewidth(0.5)

    # Plot each design
    for design, color, label in zip(designs, colors, design_labels):
        ax.plot(theta, design, color=color, linewidth=2, label=label, alpha=0.7)
        ax.fill(theta, design, color=color, alpha=0.25)

    # Set parameter labels and custom tick labels
    for i, (min_val, max_val, angle, param_label) in enumerate(
        zip(
            [r[0] for r in param_ranges],
            [r[1] for r in param_ranges],
            theta,
            param_labels,
        )
    ):
        # Construct bold parameter labels without nested $
        ax.text(angle, 1.25, param_label, ha="center", va="center", fontsize=10)

        # Bold tick labels
        for ytick in [0.25, 0.5, 0.75, 1]:
            label_val = custom_tick_formatter(ytick, min_val, max_val)
            label_text = r"$\mathbf{" + label_val + r"}$"
            ax.text(
                angle, ytick - 0.03, label_text, ha="center", va="center", fontsize=10
            )

    # Align grid lines with parameters
    ax.set_thetagrids(np.degrees(theta), [])


def create_bar_chart(
    ax,
    bar_scores_list,
    bar_errors_list,
    bar_labels,
    design_colors,
    hatches=None,
    xlabel="Score",
    title=None,
    group_labels=None,
    invert_xaxis=False,
):
    """
    Plot a horizontal bar chart with multiple bar groups and error bars.

    Args:
        ax (matplotlib.axes.Axes): The Axes object to plot on.
        bar_scores_list (list of list): Each sublist contains scores for a bar group.
        bar_errors_list (list of list): Each sublist contains std devs for a bar group.
        bar_labels (list): Labels for each bar (e.g., Design names).
        design_colors (list): Colors for each design (should match the number of bars).
        hatches (list of str, optional): Hatching patterns for each bar group.
        xlabel (str): Label for the x-axis.
        title (str, optional): Title of the bar chart.
        group_labels (list of str, optional): Labels for each bar group (e.g., ['Simulation', 'Real-World']).
        invert_xaxis (bool): Whether to invert the x-axis to start at zero and extend negatively. Default is False.
    """
    num_groups = len(bar_scores_list)
    bar_width = 0.8 / num_groups  # Total width per group is 0.8

    index = np.arange(len(bar_labels))

    for i, (bar_scores, bar_errors) in enumerate(zip(bar_scores_list, bar_errors_list)):
        # Offset for each group
        offset = (i - num_groups / 2) * bar_width + bar_width / 2
        bars = ax.barh(
            index + offset,
            bar_scores,
            bar_width,
            xerr=bar_errors,
            capsize=5,
            color=design_colors,
            edgecolor="black",
            hatch=hatches[i] if hatches and i < len(hatches) else None,
            label=group_labels[i] if group_labels and i < len(group_labels) else None,
        )

    # Add legend with hatching if group_labels are provided
    if group_labels:
        legend_elements = []
        for i, label in enumerate(group_labels):
            hatch = hatches[i] if hatches and i < len(hatches) else None
            legend_elements.append(
                Patch(facecolor="white", edgecolor="black", hatch=hatch, label=label)
            )
        ax.legend(handles=legend_elements)

    # Add labels and title
    ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)
    ax.set_yticks(index)
    ax.set_yticklabels(bar_labels)
    ax.invert_yaxis()  # Highest scores on top

    # Add grid lines on x-axis for better readability
    ax.xaxis.grid(True, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    # Customize spines
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_visible(True)
    ax.spines["bottom"].set_visible(True)

    # Handle inverted x-axis if required
    if invert_xaxis:
        ax.invert_xaxis()  # Invert the x-axis
        ax.set_xlim(left=0)  # Ensure 0 is at the left


def plot_combined_charts(
    radar_params,
    radar_ranges,
    radar_designs,
    radar_design_labels,
    radar_colors,
    bar_scores_list=None,
    bar_errors_list=None,
    bar_labels=None,
    design_colors=None,
    hatches=None,
    group_labels=None,
    radar_title="Design Parameters",
    bar_title="Design Scores",
    bar_xlabel="Energy Usage per Meter [J/m]",
    invert_xaxis=False,
):
    """
    Create a combined radar and bar chart supporting multiple bar groups with error bars.

    Args:
        radar_params (list): Names of the parameters (including units).
        radar_ranges (list of tuple): (min, max) for each radar parameter.
        radar_designs (list of list): Normalized designs to plot on radar chart.
        radar_design_labels (list): Labels for each design.
        radar_colors (list): Colors for each design.
        bar_scores_list (list of list, optional): List containing lists of scores for each bar group.
        bar_errors_list (list of list, optional): List containing lists of std deviations for each bar group.
        bar_labels (list, optional): Labels for each bar.
        design_colors (list, optional): Colors for the bars.
        hatches (list of str, optional): Hatching patterns for each bar group.
        group_labels (list of str, optional): Labels for each bar group (e.g., ['Simulation', 'Real-World']).
        radar_title (str): Title for radar chart.
        bar_title (str): Title for bar chart.
        bar_xlabel (str): Label for the x-axis of the bar chart.
    """
    NUM_PARAMS = len(radar_params)
    theta = radar_factory(NUM_PARAMS)

    # Adjusted figure size to be wider and less tall
    fig = plt.figure(figsize=(11, 3))  # Width: 11 inches, Height: 3 inches
    gs = GridSpec(1, 2, width_ratios=[3, 2], wspace=0.4)

    # ------------------------------
    # Radar Chart Subplot
    # ------------------------------
    ax_radar = fig.add_subplot(gs[0], projection="radar")
    create_radar_chart(
        ax_radar,
        theta,
        radar_designs,
        radar_colors,
        radar_design_labels,
        radar_params,
        radar_ranges,
    )
    # Optionally add radar title
    if radar_title:
        ax_radar.set_title(radar_title, fontsize=10, fontweight="bold", y=1.1)

    # ------------------------------
    # Bar Chart Subplot
    # ------------------------------
    ax_bar = fig.add_subplot(gs[1])

    if (
        bar_scores_list is not None
        and design_colors is not None
        and bar_labels is not None
        and bar_errors_list is not None
    ):
        # Plot multiple bar groups with error bars
        create_bar_chart(
            ax_bar,
            bar_scores_list,
            bar_errors_list,
            bar_labels,
            design_colors,
            hatches=hatches,
            xlabel=bar_xlabel,
            title=bar_title,
            group_labels=group_labels,
            invert_xaxis=invert_xaxis,
        )
    else:
        raise ValueError("Insufficient data provided for bar chart plotting.")

    # Adjust layout for better spacing
    plt.tight_layout()

    # plt.show()


def create_boxplot(
    ax,
    perc_diffs,
    fixed_labels,
    design_colors,
    group_y=0.3,
    box_width=0.4,
    showfliers=True,
    xlabel=None,
    ylabel=None,
    y_lim=(0, 2),
):
    """
    Create a horizontal box plot for percentage differences with highlighted fixed designs.
    This version aligns the styling with the bar chart code and uses thicker lines for the box plot
    and vertical design lines.

    Args:
        ax (matplotlib.axes.Axes): The axis object to plot on.
        perc_diffs (list of float): List of percentage differences to plot.
        fixed_labels (list of str): Labels for the fixed designs.
        design_colors (list): Colors for the fixed designs (should match the number of fixed labels).
        group_y (float, optional): y-position for the box plot. Defaults to 0.3.
        box_width (float, optional): Width of the box plot. Defaults to 0.4.
        showfliers (bool, optional): Whether to display outliers. Defaults to True.
        xlabel (str, optional): Label for the x-axis.
        ylabel (str, optional): Label for the y-axis.
        y_lim (tuple, optional): y-axis limits. Defaults to (0, 2).

    Returns:
        None
    """
    # Draw the horizontal box plot at the specified y-position.
    bp = ax.boxplot(
        perc_diffs,
        patch_artist=True,
        widths=box_width,
        showfliers=showfliers,
        vert=False,
        positions=[group_y],
    )

    # Set a consistent face color and thicker outlines for the box.
    for box in bp["boxes"]:
        box.set_facecolor("lightgray")
        box.set_linewidth(1)

    # Increase the linewidth for medians, whiskers, and caps.
    for median in bp["medians"]:
        median.set_linewidth(1)
    for whisker in bp["whiskers"]:
        whisker.set_linewidth(1)
    for cap in bp["caps"]:
        cap.set_linewidth(1)

    # Compute the range of the data to determine annotation offsets.
    data_range = max(perc_diffs) - min(perc_diffs)
    if data_range == 0:
        data_range = 1  # Prevent division by zero in the offset calculation.

    # Highlight fixed designs: draw a thicker vertical line at each fixed difference and annotate.
    num_fixed = len(fixed_labels)
    for i in range(num_fixed):
        fixed_diff = perc_diffs[i]
        # Draw a vertical line with thicker linewidth.
        ax.axvline(x=fixed_diff, linestyle="-", color=design_colors[i], linewidth=2)

        # Adjust the annotation position based on the design index.
        if i == 2:
            # For the third fixed design, shift the label slightly to the left.
            annotation_x = fixed_diff - 0.01 * data_range
            ha = "right"
        else:
            # For the others, shift the label slightly to the right.
            annotation_x = fixed_diff + 0.025 * data_range
            ha = "center"

        # Annotate the vertical line with the fixed label.
        ax.text(
            annotation_x,
            group_y + 0.7,
            fixed_labels[i],
            color=design_colors[i],
            horizontalalignment=ha,
            verticalalignment="bottom",
        )

    # Set the axis labels and limits.
    ax.set_xlabel(xlabel)
    if ylabel:
        ax.set_ylabel(ylabel)
    ax.set_ylim(*y_lim)
    ax.set_yticks([])

    # Add grid lines for better readability.
    ax.xaxis.grid(True, color="gray", linestyle="--", linewidth=0.5, alpha=0.7)
    ax.set_axisbelow(True)

    # Customize spines to match the bar chart styling.
    for spine in ["top", "right"]:
        ax.spines[spine].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_visible(True)


def create_distribution_plot(
    ax, data, fixed_labels, design_colors, xlabel=None, title=None, bins=25, kde=False
):
    from scipy.stats import gaussian_kde

    data_range = max(data) - min(data)
    y_max = None

    if kde:
        kde_estimator = gaussian_kde(data)
        x_vals = np.linspace(min(data), max(data), 200)
        y_vals = kde_estimator(x_vals)

        # KDE line without fill
        ax.plot(x_vals, y_vals, color="black", linewidth=1.5)
        y_max = max(y_vals)
    else:
        counts, bins, _ = ax.hist(
            data, bins=bins, color="white", edgecolor="black", alpha=1
        )
        y_max = max(counts)

    ax.set_ylabel("Probability Density")

    # Vertical lines for fixed designs
    for i in range(len(fixed_labels)):
        fixed_diff = data[i]
        ax.axvline(x=fixed_diff, linestyle="-", color=design_colors[i], linewidth=1.8)

        # for metric
        # Adjust label position
        if i == 1 or i == 3:  # Place d_2^n and d_1^* on the left
            annotation_x = fixed_diff - 0.02 * data_range
            ha = "right"
        else:
            annotation_x = fixed_diff + 0.02 * data_range
            ha = "left"

        ax.text(
            annotation_x,
            y_max * 0.5,
            fixed_labels[i],
            color=design_colors[i],
            ha=ha,
            va="bottom",
        )

        # for reward
        # Adjust label position
        # if i == 1:  # Place d_2^n slightly higher and on the left
        #     annotation_x = fixed_diff - 0.02 * data_range
        #     ha = 'right'
        #     ax.text(annotation_x, y_max * 0.575, fixed_labels[i],  # Adjust y_max to 0.6
        #         color=design_colors[i], ha=ha, va='bottom')
        # elif i == 2:  # Place d_1^* on the left
        #     annotation_x = fixed_diff - 0.02 * data_range
        #     ha = 'right'
        #     ax.text(annotation_x, y_max * 0.425, fixed_labels[i],
        #         color=design_colors[i], ha=ha, va='bottom')
        # elif i == 3: # Place d_2^* slightly lower and on the right
        #     annotation_x = fixed_diff - 0.02 * data_range
        #     ha = 'right'
        #     ax.text(annotation_x, y_max * 0.5, fixed_labels[i],  # Adjust y_max to 0.4
        #         color=design_colors[i], ha=ha, va='bottom')
        # else:
        #     annotation_x = fixed_diff + 0.02 * data_range
        #     ha = 'left'
        #     ax.text(annotation_x, y_max * 0.5, fixed_labels[i],
        #         color=design_colors[i], ha=ha, va='bottom')

    # Axes labels and limits
    if xlabel:
        ax.set_xlabel(xlabel)
    if title:
        ax.set_title(title)

    ax.set_xlim(min(data) - 0.5, max(data) + 0.5)
    ax.set_ylim(bottom=0)

    # Grid and spine aesthetics
    ax.xaxis.grid(True, linestyle="--", linewidth=0.6, alpha=0.5)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
