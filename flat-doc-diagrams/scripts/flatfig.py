"""Flat pastel block-diagram helpers for Chinese technical documents (Word / PDF).

Coordinates: a canvas is W x H units, 1 unit = 1 px at dpi 100, y grows downward.
Convention: W = 2000 for any figure inserted at full text width (about 15.4 cm on A4).
save() lints the drawing and prints [flatfig] warnings; fix every warning before delivering.
"""
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.font_manager import FontProperties  # noqa: E402
from matplotlib.patches import Circle, Polygon, Rectangle  # noqa: E402

TEXT = "#1F2937"
SUBTEXT = "#4B5563"
ARROW = "#374151"
LOOP = "#5B3A8C"
MUTED = "#6B7280"

PALETTE = {
    "blue": {"label": "#BDE6F4", "panel": "#EEF7FB", "box": "#93D4EB"},
    "green": {"label": "#D8EBC5", "panel": "#F3F8EE", "box": "#ADD98E"},
    "yellow": {"label": "#FFE19F", "panel": "#FFF8E5", "box": "#FFCA58"},
    "purple": {"label": "#E4D5F2", "panel": "#F6F0FB", "box": "#CEB4E6"},
    "gray": {"label": "#CDD9E7", "panel": "#F2F5F8", "box": "#DDE5EE"},
    "pink": {"label": "#F5CBD5", "panel": "#FCEFF2", "box": "#F2B8C6"},
}
STAGE = [("#CDE6BC", "#E5F2DC"), ("#BFDFF1", "#DCEEF8"), ("#F9E29A", "#FDF1C8"), ("#F1C4CF", "#F8E1E6")]
ACCENT = {"blue": "#5AB4D6", "green": "#7DB55A", "yellow": "#D9A93A", "purple": LOOP, "gray": "#8EA3BC",
          "pink": "#D98AA0"}

# Width-2000 canvas saved at dpi 200 and inserted at 15.4 cm: printed pt ~= 0.485 x size.
FONT_SCALE = 1.6
FIT_MARGIN = 0.9
SHRINK_WARN = 0.95
MAX_ASPECT = 3.2
EDGE = 3

_FONT_CANDIDATES = [
    (r"C:\Windows\Fonts\msyh.ttc", r"C:\Windows\Fonts\msyhbd.ttc"),
    ("/System/Library/Fonts/PingFang.ttc", "/System/Library/Fonts/PingFang.ttc"),
    ("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc", "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"),
    ("/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", "/usr/share/fonts/noto-cjk/NotoSansCJK-Bold.ttc"),
]


def _load_fonts():
    for regular, bold in _FONT_CANDIDATES:
        if Path(regular).exists():
            return FontProperties(fname=regular), FontProperties(fname=bold if Path(bold).exists() else regular)
    raise FileNotFoundError("No CJK font found: install Microsoft YaHei or Noto Sans CJK and add it to _FONT_CANDIDATES")


REGULAR, BOLD = _load_fonts()


def _warn(message):
    print(f"[flatfig] {message}")


def canvas(width, height):
    fig = plt.figure(figsize=(width / 100, height / 100), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, width)
    ax.set_ylim(height, 0)
    ax.axis("off")
    ax.flat_boxes, ax.flat_segments, ax.flat_free_texts, ax.flat_shrunk = [], [], [], []
    return fig, ax


def rect(ax, x, y, w, h, fill, edge="none", lw=0.0, style="-", z=1):
    ax.add_patch(Rectangle((x, y), w, h, facecolor=fill, edgecolor=edge, linewidth=lw, linestyle=style, zorder=z))


def _fit(ax, label, w, h):
    renderer = ax.figure.canvas.get_renderer()
    extent = label.get_window_extent(renderer)
    (x0, y0), (x1, y1) = ax.transData.transform([(0, 0), (w, h)])
    ratio = min(1.0, abs(x1 - x0) * FIT_MARGIN / extent.width, abs(y1 - y0) * FIT_MARGIN / extent.height)
    if ratio < 1.0:
        label.set_fontsize(label.get_fontsize() * ratio)
    if ratio < SHRINK_WARN:
        ax.flat_shrunk.append(label.get_text())
        _warn(f"text {label.get_text()!r} shrunk to {ratio:.0%}: widen/heighten the box or shorten the text")


def text(ax, x, y, s, size=14, bold=True, color=TEXT, ha="center", va="center", z=6, fit=None, free=True):
    """Text at a data point. fit=(w, h) shrinks it to fit; free texts are linted against boxes and lines."""
    label = ax.text(x, y, s, fontproperties=BOLD if bold else REGULAR, fontsize=size * FONT_SCALE, color=color,
                    ha=ha, va=va, zorder=z, linespacing=1.3)
    if fit is not None:
        _fit(ax, label, *fit)
    if free:
        ax.flat_free_texts.append(label)
    return label


def note(ax, x, y, s, size=11, ha="center"):
    """Small regular gray annotation beside an arrow or under a box."""
    return text(ax, x, y, s, size=size, bold=False, color=SUBTEXT, ha=ha)


def box(ax, x, y, w, h, s, fill, size=14, bold=True, color=TEXT, z=2, edge=None):
    """Filled block with centered text; edge gives the white outlined variant used for sub-steps."""
    rect(ax, x, y, w, h, fill, edge=edge or "none", lw=2.0 if edge else 0.0, z=z)
    ax.flat_boxes.append((x, y, w, h, s))
    return text(ax, x + w / 2, y + h / 2, s, size=size, bold=bold, color=color, z=z + 4, fit=(w, h), free=False)


def label_column(ax, x, y, w, h, s, fill, size=20):
    return box(ax, x, y, w, h, s, fill, size=size)


def layer(ax, y, h, name, family, label_w=220, x=30, gap=40, right=1970, size=20):
    """Left label column plus a light panel band; returns (panel_x, panel_w) for placing boxes."""
    label_column(ax, x, y, label_w, h, name, PALETTE[family]["label"], size=size)
    panel_x = x + label_w + gap
    rect(ax, panel_x, y, right - panel_x, h, PALETTE[family]["panel"])
    return panel_x, right - panel_x


def row_boxes(ax, x, y, w, h, names, fill, gap=30, size=14, bold=True):
    """Evenly spaced boxes across width w starting at x; returns their x centers."""
    width = (w - gap * (len(names) - 1)) / len(names)
    centers = []
    for i, name in enumerate(names):
        left = x + i * (width + gap)
        box(ax, left, y, width, h, name, fill, size=size, bold=bold)
        centers.append(left + width / 2)
    return centers


def _segments(ax, pts):
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        if x1 != x2 and y1 != y2:
            _warn(f"diagonal segment {(x1, y1)}->{(x2, y2)}: route connectors with horizontal/vertical runs only")
        ax.flat_segments.append(((x1, y1), (x2, y2)))


def line(ax, pts, color=ARROW, lw=2.0, dashed=False):
    _segments(ax, pts)
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=color, lw=lw, ls="--" if dashed else "-", solid_capstyle="butt", zorder=4)


def path_arrow(ax, pts, color=ARROW, lw=2.0, dashed=False, both=False):
    """Orthogonal polyline with an arrow head at its end (both=True: at both ends); start/end on box edge midpoints."""
    _segments(ax, pts)
    style = "--" if dashed else "-"

    def head(tail, tip, arrowstyle):
        ax.annotate("", xy=tip, xytext=tail, zorder=5,
                    arrowprops={"arrowstyle": arrowstyle, "color": color, "lw": lw, "ls": style,
                                "shrinkA": 0, "shrinkB": 0, "mutation_scale": 18})

    plain = list(zip(pts[:-2], pts[1:-1]))
    if both and plain:
        head(pts[1], pts[0], "-|>")
        plain = plain[1:]
    for (x1, y1), (x2, y2) in plain:
        ax.plot([x1, x2], [y1, y2], color=color, lw=lw, ls=style, solid_capstyle="butt", dash_capstyle="butt",
                zorder=4)
    head(pts[-2], pts[-1], "<|-|>" if both and len(pts) == 2 else "-|>")


def diamond(ax, x, y, w, h, s, fill, size=13):
    """Decision node inside the (x, y, w, h) box; vertices are the top/right/bottom/left ports."""
    cx, cy = x + w / 2, y + h / 2
    ax.add_patch(Polygon([(cx, y), (x + w, cy), (cx, y + h), (x, cy)], closed=True, facecolor=fill,
                         edgecolor="none", zorder=2))
    ax.flat_boxes.append((x, y, w, h, s))
    return text(ax, cx, cy, s, size=size, z=6, fit=(w * 0.55, h * 0.5), free=False)


def junction(ax, cx, cy, r=24):
    """Summing point of a control-style closed loop (circle with a cross)."""
    ax.add_patch(Circle((cx, cy), r, facecolor="#FFFFFF", edgecolor=ARROW, lw=2.0, zorder=3))
    d = r * 0.7071
    for sx, sy, ex, ey in ((cx - d, cy - d, cx + d, cy + d), (cx - d, cy + d, cx + d, cy - d)):
        ax.plot([sx, ex], [sy, ey], color=ARROW, lw=2.0, zorder=4)


def bracket(ax, x0, x1, y, label, color=LOOP, size=14):
    """Highlight bracket over a group of boxes, e.g. the current implementation focus."""
    line(ax, [(x0, y + 15), (x0, y), (x1, y), (x1, y + 15)], color=color, lw=2.4)
    text(ax, (x0 + x1) / 2, y - 24, label, size=size, color=color)


def _inside(seg, rx, ry, rw, rh, margin=EDGE):
    (x1, y1), (x2, y2) = seg
    ax0, ax1, ay0, ay1 = rx + margin, rx + rw - margin, ry + margin, ry + rh - margin
    if x1 == x2:
        return ax0 < x1 < ax1 and max(min(y1, y2), ay0) < min(max(y1, y2), ay1)
    if y1 == y2:
        return ay0 < y1 < ay1 and max(min(x1, x2), ax0) < min(max(x1, x2), ax1)
    return False


def _data_bbox(ax, label, renderer):
    (x0, y0), (x1, y1) = ax.transData.inverted().transform(label.get_window_extent(renderer).get_points())
    return min(x0, x1), min(y0, y1), abs(x1 - x0), abs(y1 - y0)


def lint(fig, ax):
    """Report shrunk text, connectors through boxes, overlapping boxes, clipped text and labels on boxes or lines."""
    count = len(ax.flat_shrunk)
    for seg in ax.flat_segments:
        for x, y, w, h, s in ax.flat_boxes:
            if _inside(seg, x, y, w, h):
                _warn(f"connector {seg} runs through box {s!r}")
                count += 1
    boxes = ax.flat_boxes
    for i, (x, y, w, h, s) in enumerate(boxes):
        for x2, y2, w2, h2, s2 in boxes[i + 1:]:
            if x + EDGE < x2 + w2 and x2 + EDGE < x + w and y + EDGE < y2 + h2 and y2 + EDGE < y + h:
                _warn(f"boxes {s!r} and {s2!r} overlap")
                count += 1
    renderer = fig.canvas.get_renderer()
    width, height = ax.get_xlim()[1], ax.get_ylim()[0]
    if width / height > MAX_ASPECT:
        _warn(f"canvas {width:.0f}x{height:.0f} is flatter than {MAX_ASPECT}:1 and prints too short; "
              "wrap the chain into two rows or a U-turn")
        count += 1
    for label in ax.texts:
        x, y, w, h = _data_bbox(ax, label, renderer)
        if x < 0 or y < 0 or x + w > width or y + h > height:
            _warn(f"text {label.get_text()!r} is clipped by the canvas edge")
            count += 1
    for label in ax.flat_free_texts:
        x, y, w, h = _data_bbox(ax, label, renderer)
        hits = [s for bx, by, bw, bh, s in boxes if x < bx + bw and bx < x + w and y < by + bh and by < y + h]
        hits += [str(seg) for seg in ax.flat_segments if _inside(seg, x, y, w, h, margin=1)]
        if hits:
            _warn(f"label {label.get_text()!r} overlaps {hits[0]}: move it beside the line/box")
            count += 1
    return count


def save(fig, path, dpi=200):
    ax = fig.axes[0]
    warnings = lint(fig, ax)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor="white")
    plt.close(fig)
    print(f"saved {path} ({warnings} lint warnings)")
    return warnings
