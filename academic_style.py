"""
academic_style.py - 科研论文绘图学术皮肤 (Academic Plot Style)

一个零依赖(仅 matplotlib)的通用配色/样式工具:
  - apply_academic_style()  一键期刊风: Arial / 去顶右边框 / 刻度朝外 / 300dpi / PDF 矢量
  - save_fig()              PNG(位图) + PDF(矢量) 双输出, 投稿友好
  - shade()                 同色系调浅/调深 (主线 -> 置信带 -> 浅底)
  - significance_stars()    p 值转标准星标
  - annotate_significance() 图上画显著性括号 + 星标
  - ACADEMIC_COLORS         Okabe-Ito 色盲友好色板 (另有 2 套配色可选)

用法:
    from academic_style import *
    apply_academic_style()
    fig, ax = plt.subplots()
    ...
    save_fig(fig, "figure1", output_dir="D:/project/figs")

License: MIT (c) 2026 Luoyuexin
"""
from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt

__version__ = "1.0.0"

# ------------------------------------------------------------------ 色板
# Okabe-Ito: 色盲友好, 学术投稿首选
ACADEMIC_COLORS = {"flat": "#0072B2", "mod": "#E69F00", "tv": "#009E73"}
PALETTES = {
    "okabe-ito": ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7", "#56B4E9"],
    "nature":    ["#2A6F97", "#E07A5F", "#5E9C76", "#9B7EDE", "#D9A441", "#708B91"],
    "mono":      ["#222222", "#666666", "#999999", "#444444", "#888888", "#BBBBBB"],
}


def shade(hex_color: str, factor: float) -> str:
    """调色阶: factor>1 混白(变浅), 0<factor<1 混黑(变深)。

    同色系分层是论文图表的常用手法: 主线用原色, 置信带用浅色,
    观测点用深色 —— 视觉上归为一组, 又不互相抢戏。
    """
    h = hex_color.lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) for i in (0, 2, 4))
    if factor >= 1:
        t = 1 - 1 / factor
        r, g, b = (c + (255 - c) * t for c in (r, g, b))
    else:
        r, g, b = (c * factor for c in (r, g, b))
    return "#{:02X}{:02X}{:02X}".format(*(int(round(c)) for c in (r, g, b)))


def significance_stars(p: float) -> str:
    """p 值 -> 星标: *** p<0.001, ** p<0.01, * p<0.05, '' 不显著。"""
    if p < 0.001:
        return "***"
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    return ""


# ------------------------------------------------------------------ 样式
def apply_academic_style(style: str = "default", *, palette: str = "okabe-ito") -> None:
    """一键期刊风 rcParams。

    Parameters
    ----------
    style : {"default", "compact"}
        "compact" 字号更小、线更细, 适合多子图拼版。
    palette : {"okabe-ito", "nature", "mono"}
        全局循环色板; "mono" 灰度适合黑白打印。
    """
    if palette not in PALETTES:
        raise ValueError(f"palette must be one of {sorted(PALETTES)}, got {palette!r}")
    compact = style == "compact"
    base = 7.5 if compact else 8.5
    plt.rcParams.update({
        "font.family": "sans-serif",
        "font.sans-serif": ["Arial", "Helvetica", "Segoe UI", "DejaVu Sans"],
        "font.size": base,
        "axes.titlesize": base + 1,
        "axes.titleweight": "bold",
        "axes.labelsize": base + 0.5,
        "axes.linewidth": 0.7 if compact else 0.8,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.prop_cycle": plt.cycler(color=PALETTES[palette]),
        "xtick.direction": "out",
        "ytick.direction": "out",
        "xtick.labelsize": base - 0.5,
        "ytick.labelsize": base - 0.5,
        "xtick.major.width": 0.7 if compact else 0.8,
        "ytick.major.width": 0.7 if compact else 0.8,
        "xtick.major.size": 3,
        "ytick.major.size": 3,
        "legend.fontsize": base - 0.5,
        "legend.frameon": False,
        "legend.handlelength": 1.8,
        "lines.linewidth": 1.4 if compact else 1.6,
        "lines.markersize": 3.5 if compact else 4,
        "mathtext.fontset": "stix",
        "figure.dpi": 110,
        "savefig.dpi": 300,
        "savefig.bbox": "tight",
        "pdf.fonttype": 42,   # TrueType 嵌入, 期刊投稿常见硬要求
        "ps.fonttype": 42,
    })


# ------------------------------------------------------------------ 输出
def save_fig(fig, name: str, output_dir: str | Path = ".", *,
             formats: tuple[str, ...] = ("png", "pdf"), dpi: int = 300) -> list[Path]:
    """双输出位图+矢量图, 返回生成的文件路径列表。

    Examples
    --------
    >>> save_fig(fig, "figure1", output_dir="D:/project/figs")
    """
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    saved = []
    for fmt in formats:
        path = out / f"{name}.{fmt}"
        fig.savefig(path, dpi=dpi)
        saved.append(path)
    plt.close(fig)
    return saved


# ------------------------------------------------------------------ 标注
def annotate_significance(ax, x1: float, x2: float, y: float, p: float, *,
                          text_dy: float = 0.02, height: float = 0.012,
                          lw: float = 0.8, color: str = "black",
                          fontsize: float = 10) -> bool:
    """在图上画显著性括号 + 星标, 返回是否标注。

    x1, x2 : 括号两端的横坐标 (数据坐标)
    y      : 括号基准高度 (数据坐标)
    例如组间比较: annotate_significance(ax, 1, 3, ymax*1.05, p_value)
    """
    stars = significance_stars(p)
    if not stars:
        return False
    h = height * (ax.get_ylim()[1] - ax.get_ylim()[0])
    ax.plot([x1, x1, x2, x2], [y, y + h, y + h, y],
            lw=lw, color=color, clip_on=False)
    ax.text((x1 + x2) / 2, y + h + text_dy * (ax.get_ylim()[1] - ax.get_ylim()[0]),
            stars, ha="center", va="bottom", fontsize=fontsize,
            fontweight="bold", color=color)
    return True
