import pickle
import os
import numpy as np

# Define the list of pickle file paths
file_paths = [
    "data/figure_3/evaluated_designs/evaluated_designs_policy1.pkl",
    "data/figure_3/evaluated_designs/evaluated_designs_policy4.pkl",
]

for file_path in file_paths:
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue

    with open(file_path, "rb") as f:
        data = pickle.load(f)

    print(f"\n=== Loaded {file_path} ===")
    for policy, designs in data.items():
        print(f"\n--- POLICY: {policy.upper()} ---")
        for design_name, design_info in designs.items():

            # 1) score and its std
            score = float(design_info.get("score", 0).item())
            score_std = float(design_info.get("score_std", 0).item())
            print(f"\nDesign: {design_name}")
            print(f"  Score            : {score:.5f} ± {score_std:.5f}  (J/m)")

            # 2) distance statistics
            distances = np.array(design_info.get("distance", []), dtype=float)
            dist_mean = distances.mean()
            dist_std = distances.std()
            print(f"  Distance         : {dist_mean:.5f} ± {dist_std:.5f}  (m)")

            # 3) convert score from J/m to Wh/m, then compute energies (Wh)
            score_wh_per_m = score / 3600.0
            score_std_wh_per_m = score_std / 3600.0

            # energy for each sample: Wh = (J/m → Wh/m) * m
            energies_wh = distances * score_wh_per_m

            energy_mean = energies_wh.mean()
            energy_std = energies_wh.std()

            print(
                f"  Energy per m     : {score_wh_per_m:.8f} ± {score_std_wh_per_m:.8f}  (Wh/m)"
            )
            print(f"  Energy (Wh)      : {energy_mean:.5f} ± {energy_std:.5f}  (Wh)")

            # if you want to inspect the full array, uncomment:
            # print("  All energy samples (Wh):", energies_wh)
