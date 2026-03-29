# Learning Purposeful Co-designs of Bio-inspired Quadrupedal Robots

**Fabio Boekel, Jiatao Ding*, Cosimo Della Santina**  
1. Department of Cognitive Robotics, ME, Delft University of Technology, The Netherlands  
2. Department of Industrial Engineering, University of Trento, Italy  
3. Institute of Robotics and Mechatronics, German Aerospace Center (DLR), Germany  
*Corresponding author: jiatao.ding@unitn.it

---

## Overview

This repository contains the date of the experiments, and the code to process this data for the paper:

> **Learning Purposeful Co-designs of Bio-inspired Quadrupedal Robots**

The project introduces a co-design pipeline for quadrupedal robots, jointly optimizing both morphology and control. The approach is validated on a custom modular quadruped platform, "Dogger," and demonstrates significant real-world efficiency gains through hardware experiments.

## Repository Structure

- `data/` — Raw and processed data for experiments and figures
- `experiments/` — Experiment scripts and configuration files
- `plots/` — Output plots for figures in the paper
- `utils/` — Utility functions for data loading and plotting

---

## Getting Started

### Installation

To set up your environment and install all dependencies with conda:

```bash
conda env create -f environment.yml
conda activate dogger_data_plots
```

This will create a conda environment named `dogger_data_plots` and install all required packages.

### Data
All data required to reproduce the main results and figures is included in the `data/` directory.

### Reproducing Figures
Example: To generate the energy consumption plot for the Jetson electronics (Figure S3):

```bash
python experiments/figure_s3_electronics_energy/plot_energy_jetson_only.py
```

Output will be saved to `plots/figure_s3/energy_jetson_only.pdf`.

---

## License
This project is open-source. See the LICENSE file for details.
