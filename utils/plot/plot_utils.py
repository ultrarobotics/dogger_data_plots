import os
import matplotlib.pyplot as plt
from matplotlib import rcParams

plt.rc("text", usetex=True)
plt.rc("font", family="serif", serif="Times", size=10)
rcParams["text.latex.preamble"] = r"""
    \usepackage{amsmath}
    \usepackage{amssymb}
    \usepackage{wasysym}
    \usepackage{mathptmx}
"""


def save_plot(fig, file_path, dpi=300, tight=True):
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    if tight:
        fig.tight_layout()
    fig.savefig(file_path, dpi=dpi, bbox_inches="tight")
    print(f"Plot saved to {file_path}")
    plt.close(fig)
