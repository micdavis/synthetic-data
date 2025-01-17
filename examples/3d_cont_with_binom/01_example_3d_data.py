#!/usr/bin/env python


"""
Test mapping y = f(X)
"""
from synthetic_data.synthetic_data import make_tabular_data
import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from math import pi
import pickle

import pathlib

from synthetic_data.utils import resolve_output_path

output_path = resolve_output_path(pathlib.Path(__file__).parent.absolute())

# define expression
# expr = x1 + 2 * x2
# expr = x1 ** 2 + 1.5 * x2 ** 2
# expr = cos(x1 * pi / 180.0) - sin(x2 * pi / 180.0)
expr = "cos(x1 ** 2 * pi / 180.0) - sin(x2 * pi / 180.0) + x1 * x2 + (0.1 * x3)"

# define mapping from symbols to column of X
col_map = {"x1": 0, "x2": 1, "x3": 2}


# define correlations via covariance matrix
cov = np.array([[1.0, 0.5, 0.1], [0.5, 1.0, 0.0], [0.1, 0.0, 1.0]])

dist = [
    {"column": 0, "dist": "norm"},
    {"column": 1, "dist": "uniform"},
    {"column": 2, "dist": "bernoulli", "args": {"p": 0.6}},
]

X, y_reg, y_prob, y_label = make_tabular_data(
    dist=dist,
    n_informative=3,
    n_samples=1000,
    cov=cov,
    col_map=col_map,
    expr=expr,
    p_thresh=0.5,
)


#
# check X
#
print("Correlation coefficients:")
print(np.corrcoef(X, rowvar=False))

h = sns.jointplot(X[:, 0], X[:, 1], kind="hex", stat_func=None)
h.set_axis_labels("x1", "x2", fontsize=16)
h.savefig(f"{output_path}/x1_x2_joint_dist_plot.png")

h = sns.jointplot(X[:, 0], X[:, 2], kind="hex", stat_func=None)
h.set_axis_labels("x1", "x3", fontsize=16)
h.savefig(f"{output_path}/x1_x3_joint_dist_plot.png")
#
# check Y
#
# paste together df to hold X, y_reg, y_prob, y_label
df = pd.DataFrame(data=X)
# df["y_reg"] = y_reg
# df["y_prob"] = y_prob
df["label"] = y_label

# summary plot
h = sns.set(style="ticks", color_codes=True)
h = sns.pairplot(
    df,
    vars=[0, 1],
    hue="label",
    markers=[".", "."],
    diag_kind="kde",
    diag_kws={"alpha": 0.5, "clip": (-1, 1)},
)
# plt.show()
h.savefig(f"{output_path}/pairplot_2D_example.png")


# save the data out to pickle files for modeling/explanations/magic!
with open("x.pkl", "wb") as f:
    pickle.dump(X, f)

with open("y_label.pkl", "wb") as f:
    pickle.dump(y_label, f)

# check contour of y_reg vs (x1, x2)
levels = np.arange(0, 2.2, 0.2)
fig, ax = plt.subplots(figsize=(8, 8))
tri1 = ax.tricontourf(X[:, 0], X[:, 1], y_reg, levels=levels)
scatter = ax.scatter(X[:, 0], X[:, 1], c=y_label, label=y_label, marker=".")
leg1 = ax.legend(*scatter.legend_elements(), loc="lower right", title="class")
cbar1 = fig.colorbar(tri1, ax=ax)
ax.set_title("y_reg contours")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
cbar1.formatter.set_powerlimits((0, 0))
cbar1.update_ticks()
fig.savefig(f"{output_path}/y_reg_contours.png")

# check contour of y_prob vs (x1, x2)
levels = np.arange(0, 1.1, 0.1)
fig, ax = plt.subplots(figsize=(8, 8))
tri1 = ax.tricontourf(X[:, 0], X[:, 1], y_prob, levels=levels)
scatter = ax.scatter(X[:, 0], X[:, 1], c=y_label, label=y_label, marker=".")
leg1 = ax.legend(*scatter.legend_elements(), loc="lower right", title="class")
cbar1 = fig.colorbar(tri1, ax=ax)
ax.set_title("y_prob contours")
ax.set_xlabel("x1")
ax.set_ylabel("x2")
cbar1.formatter.set_powerlimits((0, 0))
cbar1.update_ticks()
fig.savefig(f"{output_path}/y_prob_contours.png")


plt.show()

df = pd.DataFrame(data=X)
df.columns = ["x1", "x2", "x3"]
df["y_reg"] = y_reg
df["y_prob"] = y_prob
df["y_label"] = y_label
df.to_csv("samples.csv", index=False)
