"""
demo.py - academic-plot-style 效果展示

自包含: 固定随机种子, 仅需 matplotlib + numpy, 不读任何外部数据。
运行: python examples/demo.py
输出: examples/demo_showcase.png / .pdf
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))  # 允许直接运行

import matplotlib.pyplot as plt
import numpy as np

from academic_style import (ACADEMIC_COLORS, apply_academic_style,
                            annotate_significance, shade, significance_stars,
                            save_fig)

apply_academic_style()
rng = np.random.default_rng(42)
out = Path(__file__).resolve().parent

fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2))
fig.suptitle("academic-plot-style v1.0 — showcase", fontsize=12, fontweight="bold")

# ---- (a) 箱线+小提琴+显著性星标+同色系分层
ax = axes[0, 0]
groups = [rng.normal(2.0 + 0.7 * i, 0.55, 45) for i in range(3)]
colors = [ACADEMIC_COLORS[c] for c in ("flat", "mod", "tv")]
vp = ax.violinplot(groups, positions=[1, 2, 3], showextrema=False, widths=0.8)
for body, c in zip(vp["bodies"], colors):
    body.set_facecolor(shade(c, 1.6)); body.set_alpha(0.55)
bp = ax.boxplot(groups, positions=[1, 2, 3], widths=0.28, patch_artist=True,
                showfliers=False, showmeans=True,
                medianprops=dict(color="black", lw=1.0),
                meanprops=dict(marker="^", mfc="white", mec="black", ms=4))
for patch, c in zip(bp["boxes"], colors):
    patch.set_facecolor(c); patch.set_alpha(0.85)
    patch.set_edgecolor(shade(c, 0.6)); patch.set_linewidth(0.8)
top = max(g.max() for g in groups)
annotate_significance(ax, 1, 3, top + 0.12, 0.0034, text_dy=0.01)
ax.set_xticks([1, 2, 3]); ax.set_xticklabels(["group A", "group B", "group C"])
ax.set_ylim(0, top + 0.7)
ax.set_title("(a) box + violin, significance, shaded palette")
ax.set_ylabel("measured value")
ax.grid(False)

# ---- (b) 衰减曲线 + 置信带 + 交点标注
ax = axes[0, 1]
d = np.array([4, 8, 16, 32, 64, 128, 256], float)
for i, (name, c) in enumerate(zip(["flat", "mod", "tv"], colors)):
    a, b, cc = 0.86 - 0.02 * i, 0.0068 - 0.0018 * i, 0.02
    y = a * np.exp(-b * d) + cc
    band = 0.045 * np.sin(d / 20 + i) + 0.03
    ax.fill_between(d, y - band, y + band, color=shade(c, 2.2), alpha=0.55)
    ax.plot(d, y, color=c, lw=1.8, marker="o", ms=3.5, label=name)
    dstar = np.log((a - cc) / (0.5 - cc)) / b
    ax.plot([dstar, dstar], [0.02, 0.5], ls="--", lw=0.9, color=c, alpha=0.7)
    ax.plot(dstar, 0.5, marker="o", ms=5, mfc="white", mec=c, mew=1.2)
    ax.annotate(f"d*={dstar:.0f}m", xy=(dstar, 0.5),
                xytext=(dstar * 0.55, 0.62 + 0.05 * (i % 2)),
                fontsize=7.5, color=c, fontweight="bold")
ax.axhline(0.5, ls=":", lw=0.9, color="0.45")
ax.set_xscale("log"); ax.set_xticks(d); ax.set_xticklabels([int(x) for x in d])
ax.set_xlabel("distance (m)"); ax.set_ylabel("fidelity F(d)")
ax.set_title("(b) decay fit, CI band, annotated distance")
ax.legend(loc="lower left", ncols=2)
ax.grid(axis="y", color="0.88", lw=0.5, ls="--")

# ---- (c) 柱状图 + 全局循环色板
ax = axes[1, 0]
x = np.arange(4)
for i in range(3):
    vals = rng.uniform(0.4, 0.9, 4) + i * 0.05
    ax.bar(x + (i - 1) * 0.25, vals, 0.25, label=f"series {i + 1}",
           color=f"C{i}", edgecolor="white", lw=0.5)
ax.set_xticks(x); ax.set_xticklabels(["A", "B", "C", "D"])
ax.set_title("(c) grouped bars with global palette")
ax.set_ylabel("score")
ax.legend(fontsize=7.5)

# ---- (d) 星标速查
ax = axes[1, 1]
ax.axis("off")
ax.set_title("(d) significance_stars(p) reference")
rows = [(0.0005, "***"), (0.006, "**"), (0.03, "*"), (0.5, "(none)")]
for i, (p, s) in enumerate(rows):
    ax.text(0.08, 0.78 - i * 0.2, f"p = {p:<6} -> {s}",
            fontsize=10, family="monospace", transform=ax.transAxes)
    ax.text(0.82, 0.78 - i * 0.2, significance_stars(p),
            fontsize=11, fontweight="bold", color=colors[2], transform=ax.transAxes)

fig.tight_layout()
paths = save_fig(fig, "demo_showcase", output_dir=out)
print("[demo] " + ", ".join(p.name for p in paths))
