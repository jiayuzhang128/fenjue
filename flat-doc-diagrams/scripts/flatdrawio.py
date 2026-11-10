"""Editable .drawio output for flatfig figures.

Same functions and signatures as flatfig: a figure script switches engine by importing from
flatdrawio instead of flatfig and saving to a .drawio path. Every call also draws on a flatfig
canvas, so save() runs the flatfig lint and writes a PNG preview next to the .drawio file.

Needs flatfig.py in the same directory.
"""
import html
from datetime import datetime
from pathlib import Path
from xml.sax.saxutils import quoteattr

from matplotlib.colors import to_hex

import flatfig as ff
from flatfig import ACCENT, ARROW, LOOP, MUTED, PALETTE, STAGE, SUBTEXT, TEXT, lint  # noqa: F401

FONT = "Microsoft YaHei"
PX = 100 / 72  # matplotlib points -> canvas units (draw.io px) at dpi 100
SNAP = 1.0
TEXT_PAD_X, TEXT_PAD_Y, TEXT_WIDEN = 16, 8, 1.1
SOLID, DOTTED = ("-", "solid"), (":", "dotted")


def canvas(width, height):
    fig, ax = ff.canvas(width, height)
    ax.flat_cells = []
    return fig, ax


def _num(value):
    return "%g" % round(float(value), 2)


def _font(label, bold, color):
    return "fontFamily=%s;fontSize=%d;fontStyle=%d;fontColor=%s;" % (
        FONT, round(label.get_fontsize() * PX), 1 if bold else 0, _hex(color))


def _hex(color):
    """Any matplotlib color -> #RRGGBB, the only form draw.io styles accept."""
    return "none" if color is None or (isinstance(color, str) and color == "none") else to_hex(color).upper()


def _shape(fill, edge=None, lw=2.0, style="-"):
    stroke = "strokeColor=none;"
    if _hex(edge) != "none" and lw > 0:
        dash = "" if style in SOLID else "dashed=1;dashPattern=1 3;" if style in DOTTED else "dashed=1;"
        stroke = "strokeColor=%s;strokeWidth=%s;%s" % (_hex(edge), _num(lw * PX), dash)
    return "rounded=0;html=1;fillColor=%s;%s" % (_hex(fill), stroke)


def _vertex(ax, value, x, y, w, h, style, z, port=False):
    ax.flat_cells.append({"kind": "vertex", "value": value, "box": (x, y, w, h), "style": style, "z": z, "port": port})


def _edge(ax, pts, color, lw, dashed, start, end):
    orthogonal = all(x1 == x2 or y1 == y2 for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]))
    style = ("edgeStyle=%s;rounded=0;html=1;strokeColor=%s;strokeWidth=%s;"
             "startArrow=%s;startFill=1;endArrow=%s;endFill=1;%s"
             % ("orthogonalEdgeStyle" if orthogonal else "none", _hex(color), _num(lw * PX), start, end,
                "dashed=1;" if dashed else ""))
    ax.flat_cells.append({"kind": "edge", "pts": list(pts), "style": style, "z": 4, "port": False})


def rect(ax, x, y, w, h, fill, edge="none", lw=0.0, style="-", z=1):
    ff.rect(ax, x, y, w, h, fill, edge=edge, lw=lw, style=style, z=z)
    _vertex(ax, "", x, y, w, h, _shape(fill, edge, lw, style), z)


def text(ax, x, y, s, size=14, bold=True, color=TEXT, ha="center", va="center", z=6, fit=None, free=True):
    label = ff.text(ax, x, y, s, size=size, bold=bold, color=color, ha=ha, va=va, z=z, fit=fit, free=free)
    _, _, bw, bh = ff._data_bbox(ax, label, ax.figure.canvas.get_renderer())
    w, h = bw * TEXT_WIDEN + TEXT_PAD_X, bh + TEXT_PAD_Y
    left = {"left": x, "right": x - w}.get(ha, x - w / 2)
    top = {"top": y, "bottom": y - h}.get(va, y - h / 2)
    _vertex(ax, s, left, top, w, h,
            "text;html=1;strokeColor=none;fillColor=none;spacing=0;align=%s;verticalAlign=%s;"
            % (ha, va if va in ("top", "bottom") else "middle")
            + _font(label, bold, color), z)
    return label


def note(ax, x, y, s, size=11, ha="center"):
    return text(ax, x, y, s, size=size, bold=False, color=SUBTEXT, ha=ha)


def box(ax, x, y, w, h, s, fill, size=14, bold=True, color=TEXT, z=2, edge=None):
    label = ff.box(ax, x, y, w, h, s, fill, size=size, bold=bold, color=color, z=z, edge=edge)
    _vertex(ax, s, x, y, w, h, _shape(fill, edge) + "align=center;verticalAlign=middle;" + _font(label, bold, color),
            z, port=True)
    return label


def label_column(ax, x, y, w, h, s, fill, size=20):
    return box(ax, x, y, w, h, s, fill, size=size)


def layer(ax, y, h, name, family, label_w=220, x=30, gap=40, right=1970, size=20):
    label_column(ax, x, y, label_w, h, name, PALETTE[family]["label"], size=size)
    panel_x = x + label_w + gap
    rect(ax, panel_x, y, right - panel_x, h, PALETTE[family]["panel"])
    return panel_x, right - panel_x


def row_boxes(ax, x, y, w, h, names, fill, gap=30, size=14, bold=True):
    width = (w - gap * (len(names) - 1)) / len(names)
    centers = []
    for i, name in enumerate(names):
        left = x + i * (width + gap)
        box(ax, left, y, width, h, name, fill, size=size, bold=bold)
        centers.append(left + width / 2)
    return centers


def line(ax, pts, color=ARROW, lw=2.0, dashed=False):
    ff.line(ax, pts, color=color, lw=lw, dashed=dashed)
    _edge(ax, pts, color, lw, dashed, "none", "none")


def path_arrow(ax, pts, color=ARROW, lw=2.0, dashed=False, both=False):
    ff.path_arrow(ax, pts, color=color, lw=lw, dashed=dashed, both=both)
    _edge(ax, pts, color, lw, dashed, "block" if both else "none", "block")


def diamond(ax, x, y, w, h, s, fill, size=13):
    label = ff.diamond(ax, x, y, w, h, s, fill, size=size)
    _vertex(ax, s, x, y, w, h,
            "rhombus;perimeter=rhombusPerimeter;html=1;fillColor=%s;strokeColor=none;align=center;verticalAlign=middle;"
            % _hex(fill) + _font(label, True, TEXT), 2, port=True)
    return label


def junction(ax, cx, cy, r=24):
    ff.junction(ax, cx, cy, r=r)
    _vertex(ax, "", cx - r, cy - r, 2 * r, 2 * r,
            "shape=sumEllipse;perimeter=ellipsePerimeter;html=1;fillColor=#FFFFFF;strokeColor=%s;strokeWidth=%s;"
            % (ARROW, _num(2.0 * PX)), 3, port=True)


def bracket(ax, x0, x1, y, label, color=LOOP, size=14):
    line(ax, [(x0, y + 15), (x0, y), (x1, y), (x1, y + 15)], color=color, lw=2.4)
    text(ax, (x0 + x1) / 2, y - 24, label, size=size, color=color)


def _port(point, cells):
    """Id and relative anchor of the block whose border the point lies on, so the edge follows the block."""
    px, py = point
    for cell in reversed(cells):
        if not cell["port"]:
            continue
        x, y, w, h = cell["box"]
        on_x = min(abs(px - x), abs(px - x - w)) <= SNAP and y - SNAP <= py <= y + h + SNAP
        on_y = min(abs(py - y), abs(py - y - h)) <= SNAP and x - SNAP <= px <= x + w + SNAP
        if on_x or on_y:
            return cell["id"], "%.6g" % ((px - x) / w), "%.6g" % ((py - y) / h)
    return None


def _label(value):
    """Plain text with newlines -> HTML label, then escaped once more as an XML attribute by quoteattr."""
    return quoteattr("<br>".join(html.escape(part, quote=False) for part in value.split("\n")))


def _xml(ax, name):
    cells = sorted(ax.flat_cells, key=lambda cell: cell["z"])
    for number, cell in enumerate(cells, start=2):
        cell["id"] = "c%d" % number
    lines = []
    for cell in cells:
        if cell["kind"] == "vertex":
            x, y, w, h = (_num(v) for v in cell["box"])
            lines.append('<mxCell id="%s" value=%s style="%s" vertex="1" parent="1">'
                         '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
                         % (cell["id"], _label(cell["value"]), cell["style"], x, y, w, h))
            continue
        pts, style, ends = cell["pts"], cell["style"], ""
        for point, attr, prefix in ((pts[0], "source", "exit"), (pts[-1], "target", "entry")):
            port = _port(point, cells)
            if port:
                ends += ' %s="%s"' % (attr, port[0])
                style += "%sX=%s;%sY=%s;%sDx=0;%sDy=0;%sPerimeter=0;" % (prefix, port[1], prefix, port[2],
                                                                    prefix, prefix, prefix)
        waypoints = "".join('<mxPoint x="%s" y="%s"/>' % (_num(px), _num(py)) for px, py in pts[1:-1])
        lines.append('<mxCell id="%s" style="%s" edge="1" parent="1"%s><mxGeometry relative="1" as="geometry">'
                     '<mxPoint x="%s" y="%s" as="sourcePoint"/><mxPoint x="%s" y="%s" as="targetPoint"/>%s'
                     '</mxGeometry></mxCell>'
                     % (cell["id"], style, ends, _num(pts[0][0]), _num(pts[0][1]), _num(pts[-1][0]), _num(pts[-1][1]),
                        '<Array as="points">%s</Array>' % waypoints if waypoints else ""))
    width, height = _num(ax.get_xlim()[1]), _num(ax.get_ylim()[0])
    head = ('<mxfile host="app.diagrams.net"><diagram id="flatdoc" name=%s>'
            '<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" '
            'fold="1" page="1" pageScale="1" pageWidth="%s" pageHeight="%s" math="0" shadow="0"><root>'
            '<mxCell id="0"/><mxCell id="1" parent="0"/>' % (quoteattr(name), width, height))
    return "\n".join([head] + lines + ["</root></mxGraphModel></diagram></mxfile>"]) + "\n"


def _backup(path):
    """Rename an existing file to a .bak name that is not taken yet, so no earlier backup is overwritten."""
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    backup, number = path.with_name("%s.bak-%s" % (path.name, stamp)), 1
    while backup.exists():
        number += 1
        backup = path.with_name("%s.bak-%s-%d" % (path.name, stamp, number))
    path.rename(backup)
    print(f"[flatdrawio] existing file kept as {backup}")


def save(fig, path, dpi=200, name=None, preview=True):
    """Lint, write <stem>_preview.png and the .drawio file; an existing different file is kept as a .bak copy."""
    path = Path(path)
    if path.suffix.lower() != ".drawio":
        raise ValueError(f"flatdrawio.save() writes .drawio files, got {path.name!r}")
    ax = fig.axes[0]
    data = _xml(ax, name or path.stem).encode("utf-8")
    if preview:
        warnings = ff.save(fig, path.with_name(path.stem + "_preview.png"), dpi=dpi)
    else:
        warnings = ff.lint(fig, ax)
        ff.plt.close(fig)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() != data:
        _backup(path)
    path.write_bytes(data)
    print(f"saved {path} ({len(ax.flat_cells)} cells, {warnings} lint warnings)")
    return warnings
