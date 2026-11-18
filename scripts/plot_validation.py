"""Render the Figure 1 benchmark from the reproduced metrics table."""
import csv
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

ROOT = Path(__file__).resolve().parents[1]
with (ROOT / "results/validation/metrics.tsv").open() as handle:
    policies = {r["policy"]: r for r in csv.DictReader(handle, delimiter="\t")}
matched = policies["figure_consistent"]
literal = policies["methods_literal"]
ink, teal, amber = "#172f42", "#146c72", "#995117"
plt.rcParams.update({"font.family": "DejaVu Sans", "text.color": ink,
                     "axes.labelcolor": ink, "xtick.color": ink, "ytick.color": ink})
fig = plt.figure(figsize=(10.5, 4.8), facecolor="white")
fig.text(.035, .925, "ecDNA classifier validation", fontsize=20, weight="bold")
fig.text(.035, .853, "AmpliconClassifier v1.5.1  |  175 gene probes across 72 cell lines", fontsize=11)
fig.text(.035, .735, "A   Confusion matrix", fontsize=13, weight="bold")
fig.text(.53, .735, "B   Effect of scoring four uncertain probes", fontsize=13, weight="bold")

ax = fig.add_axes([.163, .19, .28, .42])
ax.set_xlim(0, 2)
ax.set_ylim(2, 0)
for y, keys in enumerate([("TN", "FN"), ("FP", "TP")]):
    for x, key in enumerate(keys):
        correct = key in {"TN", "TP"}
        ax.add_patch(Rectangle((x, y), 1, 1, facecolor=teal if correct else "#edf2f4",
                               edgecolor="white", linewidth=2))
        color = "white" if correct else ink
        ax.text(x+.5, y+.45, matched[key], ha="center", va="center", fontsize=20, color=color)
        ax.text(x+.5, y+.76, key, ha="center", va="center", fontsize=9, color=color)
ax.set_xticks([.5, 1.5], ["Non-ecDNA", "ecDNA"])
ax.set_yticks([.5, 1.5], ["Non-ecDNA", "ecDNA"])
ax.set_xlabel("FISH observation")
ax.set_ylabel("Classifier call")
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)

ax = fig.add_axes([.62, .19, .33, .42])
for i, metric in enumerate(["precision", "recall"]):
    for offset, rec, color, marker in [(0.14, literal, amber, "s"), (-0.14, matched, teal, "o")]:
        value = float(rec[metric])*100
        ax.scatter(value, i+offset, color=color, marker=marker, s=60)
        ax.text(value+0.7, i+offset, f"{value:.1f}%", va="center", fontsize=10, color=color)
ax.set(xlim=(80, 101), ylim=(1.5, -.5), xlabel="Percent")
ax.set_xticks([80,85,90,95,100])
ax.set_yticks([0,1], ["Precision", "Recall"])
ax.grid(axis="x", color="#e3e9ea")
ax.set_axisbelow(True)
ax.tick_params(length=0)
for spine in ax.spines.values():
    spine.set_visible(False)
fig.text(.53, .65, "■  False positives", color=amber, fontsize=10)
fig.text(.72, .65, "●  Neutral", color=teal, fontsize=10)
fig.text(.035, .037, f"Panel A uses the figure-consistent rule: {matched['scored']} probes scored, {matched['neutral']} neutral.", fontsize=10)
out = ROOT / "results/figures/figure1-validation.png"
out.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(out, dpi=180)
