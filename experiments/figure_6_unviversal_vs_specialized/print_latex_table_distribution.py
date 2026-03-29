import pickle
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"  # Suppresses TensorFlow/JAX info & warnings

# File paths and labels
# File info: (path, metric, task_id)
file_info = [
    ("data/figure_6/eval_reward_task_1.pkl", "reward", 1),
    ("data/figure_6/eval_reward_task_2.pkl", "reward", 2),
    ("data/figure_6/eval_metric_task_1.pkl", "cot", 1),
    ("data/figure_6/eval_metric_task_2.pkl", "cot", 2),
]

# Data container: design_id → fields
designs_data = {}

# Track best (max for reward, min for cot) for bolding
best_scores = {}

# Load and process all files
for file_path, metric, task_id in file_info:
    with open(file_path, "rb") as f:
        data = pickle.load(f)

    univ_keys = sorted(
        [k for k in data if k.endswith("_universal")],
        key=lambda k: int(k.split("_range")[1].split("_")[0]),
    )
    spec_keys = sorted(
        [k for k in data if k.endswith("_specialized")],
        key=lambda k: int(k.split("_range")[1].split("_")[0]),
    )
    assert len(univ_keys) == len(spec_keys)

    scores_u = [data[k]["score_mean"] for k in univ_keys]
    scores_s = [data[k]["score_mean"] for k in spec_keys]
    best_u = max(scores_u) if metric == "reward" else min(scores_u)
    best_s = max(scores_s) if metric == "reward" else min(scores_s)

    key_u = f"{metric}_pi_u_task{task_id}"
    key_s = f"{metric}_pi_s_task{task_id}"
    best_scores[key_u] = best_u
    best_scores[key_s] = best_s

    for i, (ku, ks) in enumerate(zip(univ_keys, spec_keys)):
        if i not in designs_data:
            designs_data[i] = {}
            lambda1, lambda2, lambda3, d, o = data[ku]["design"]
            designs_data[i]["design"] = (lambda1, lambda2, lambda3, d * 1000, o * 1000)

        u_val = data[ku]["score_mean"]
        s_val = data[ks]["score_mean"]

        designs_data[i][key_u] = (
            r"$\mathbf{" + f"{u_val:.2f}" + r"}$"
            if u_val == best_u
            else f"${u_val:.2f}$"
        )
        designs_data[i][key_s] = (
            r"$\mathbf{" + f"{s_val:.2f}" + r"}$"
            if s_val == best_s
            else f"${s_val:.2f}$"
        )


# Output LaTeX table
print(r"""\begin{table*}[h!]
\centering
\caption{Design parameters and task-specific performance scores using $\pi_u$ and $\pi_s$ policies.}
\resizebox{\textwidth}{!}{
\begin{tabular}{lccccc|cc|cc|cc|cc}
\hline
\multirow{2}{*}{\textbf{Design}} & \multirow{2}{*}{\(\lambda_1\)} & \multirow{2}{*}{\(\lambda_2\)} & \multirow{2}{*}{\(\lambda_3\)} & \multirow{2}{*}{\(\diameter\, [\mathrm{mm}]\)} & \multirow{2}{*}{\(o_s\, [\mathrm{mm}]\)} &
\multicolumn{2}{c|}{\textbf{Reward [-] (T1)}} & \multicolumn{2}{c|}{\textbf{Reward [-] (T2)}} &
\multicolumn{2}{c|}{\textbf{$\mathbf{CoT} [J/m]$ (T1)}} & \multicolumn{2}{c}{\textbf{$\mathbf{CoT} [J/m]$ (T2)}} \\
\cline{7-14}
& & & & & &
\textbf{$\pi_u$} & \textbf{$\pi_s$} &
\textbf{$\pi_u$} & \textbf{$\pi_s$} &
\textbf{$\pi_u$} & \textbf{$\pi_s$} &
\textbf{$\pi_u$} & \textbf{$\pi_s$} \\
\hline""")

for i, entry in designs_data.items():
    lambda1, lambda2, lambda3, d_mm, o_mm = entry["design"]
    label = (
        r"$d^n_1$"
        if i == 0
        else (
            r"$d^n_2$"
            if i == 1
            else r"$d^*_1$" if i == 2 else r"$d^*_2$" if i == 3 else rf"$d_{{{i+1}}}$"
        )
    )

    row = [
        label,
        f"${lambda1:.2f}$",
        f"${lambda2:.2f}$",
        f"${lambda3:.2f}$",
        f"${d_mm:.0f}$",
        f"${o_mm:.0f}$",
        entry.get("reward_pi_u_task1", "--"),
        entry.get("reward_pi_s_task1", "--"),
        entry.get("reward_pi_u_task2", "--"),
        entry.get("reward_pi_s_task2", "--"),
        entry.get("cot_pi_u_task1", "--"),
        entry.get("cot_pi_s_task1", "--"),
        entry.get("cot_pi_u_task2", "--"),
        entry.get("cot_pi_s_task2", "--"),
    ]
    print(" & ".join(row) + r" \\")

# Footer
print(r"""\hline
\end{tabular}
}
\label{tab:universal_specialized_grouped}
\end{table*}""")
