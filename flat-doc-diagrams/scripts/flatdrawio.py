# -*- coding: utf-8 -*-
"""flatdrawio — emit .drawio files in the flat-doc-diagrams style.

Mirrors the flatfig API (panel/labelcol/box/edge/note) so both engines share one
mental model: same geometry, same palette tints, same edge semantics. The output
is an editable .drawio (draw.io / diagrams.net) for manual fine-tuning.

Hard-won pitfalls baked in here (do not regress):
  1. <br> is escaped EXACTLY ONCE (html.escape) — double-escaping prints literal "<br>".
  2. Every text style carries fontFamily=Microsoft YaHei;fontStyle=1 (drawio default is Helvetica).
  3. Font sizes are flatfig size × 1.6 (drawio has no internal scaling).
  4. Panels never overlap the label column: panel x = label x + label_w + gap.
  5. Every edge carries explicit exit/entry anchors + waypoint points (orthogonal only).
Preview the result (same coordinates in matplotlib) before delivering.
"""
import html
from pathlib import Path

FONT = "Microsoft YaHei"
TEXT = "#1F2937"
SUBTEXT = "#4B5563"
ARROW = "#374151"

PALETTE = {
    "blue":   {"label": "#BDE6F4", "panel": "#EEF7FB", "box": "#93D4EB"},
    "green":  {"label": "#D8EBC5", "panel": "#F3F8EE", "box": "#ADD98E"},
    "yellow": {"label": "#FFE19F", "panel": "#FFF8E5", "box": "#FFCA58"},
    "purple": {"label": "#E4D5F2", "panel": "#F6F0FB", "box": "#CEB4E6"},
    "gray":   {"label": "#CDD9E7", "panel": "#F2F5F8", "box": "#DDE5EE"},
    "pink":   {"label": "#F5CBD5", "panel": "#FCEFF2", "box": "#F2B8C6"},
}

# flatfig size → drawio fontSize (×1.6, rounded)
def fs(size):
    return int(round(size * 1.6))


class Drawio:
    def __init__(self, page_w=2000, page_h=1210, name="总体架构"):
        self.pw, self.ph, self.name = page_w, page_h, name
        self.cells = []
        self._id = 1

    def _nid(self):
        self._id += 1
        return "c%d" % self._id

    def vertex(self, value, x, y, w, h, style):
        i = self._nid()
        self.cells.append(
            '<mxCell id="%s" value="%s" style="%s" vertex="1" parent="1">'
            '<mxGeometry x="%s" y="%s" width="%s" height="%s" as="geometry"/></mxCell>'
            % (i, html.escape(value, quote=False), style, x, y, w, h))
        return i

    def edge(self, src, dst, exit=(0.5, 1), entry=(0.5, 0), points=(), dashed=False, color=None):
        pts = "".join('<mxPoint x="%s" y="%s" as="point"/>' % p for p in points)
        st = ("edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;strokeColor=%s;strokeWidth=2;"
              "endArrow=block;endFill=1;fontFamily=%s;fontSize=20;"
              "exitX=%s;exitY=%s;exitDx=0;exitDy=0;entryX=%s;entryY=%s;entryDx=0;entryDy=0;"
              % (color or ARROW, FONT, exit[0], exit[1], entry[0], entry[1]))
        if dashed:
            st = ("html=1;dashed=1;strokeColor=%s;strokeWidth=1.5;endArrow=none;startArrow=none;"
                  "fontFamily=%s;fontSize=19;exitX=%s;exitY=%s;entryX=%s;entryY=%s;"
                  % (color or "#6B7280", FONT, exit[0], exit[1], entry[0], entry[1]))
        i = self._nid()
        geo = '<mxGeometry relative="1" as="geometry">'
        if pts:
            geo += '<Array as="points">%s</Array>' % pts
        geo += "</mxGeometry>"
        self.cells.append('<mxCell id="%s" style="%s" edge="1" parent="1" source="%s" target="%s">%s</mxCell>'
                          % (i, st, src, dst, geo))
        return i

    # ---- flatfig 风格便捷方法 ----
    def panel(self, x, y, w, h, fill):
        return self.vertex("", x, y, w, h,
                           "rounded=0;whiteSpace=wrap;html=1;fillColor=%s;strokeColor=none;" % fill)

    def labelcol(self, name, x, y, w, h, fill):
        return self.vertex(name, x, y, w, h,
                           "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
                           "fillColor=%s;fontColor=%s;fontSize=%d;fontStyle=1;strokeColor=none;"
                           % (fill, TEXT, fs(20)))

    def box(self, value, x, y, w, h, fill, size=14):
        return self.vertex(value, x, y, w, h,
                           "rounded=0;whiteSpace=wrap;html=1;align=center;verticalAlign=middle;"
                           "fillColor=%s;fontColor=%s;fontSize=%d;fontStyle=1;strokeColor=none;"
                           % (fill, TEXT, fs(size)))

    def note(self, value, x, y, w, size=12):
        return self.vertex(value, x, y, w, 45,
                           "text;html=1;align=left;verticalAlign=middle;fontFamily=%s;"
                           "fontColor=%s;fontSize=%d;" % (FONT, SUBTEXT, fs(size)))

    def row_boxes(self, x, y, w, h, names, fill, gap=30, size=14):
        """Evenly spaced boxes across width w; returns their ids (left to right)."""
        width = (w - gap * (len(names) - 1)) / len(names)
        ids = []
        for k, name in enumerate(names):
            ids.append(self.box(name, x + k * (width + gap), y, width, h, fill, size=size))
        return ids

    def save(self, path):
        xml = ('<mxfile host="app.diagrams.net">'
               '<diagram id="flatdoc" name="%s">'
               '<mxGraphModel dx="1400" dy="900" grid="0" gridSize="10" guides="1" tooltips="1" '
               'connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="%s" pageHeight="%s" '
               'math="0" shadow="0"><root><mxCell id="0"/><mxCell id="1" parent="0"/>'
               % (self.name, self.pw, self.ph)
               + "".join(self.cells)
               + "</root></mxGraphModel></diagram></mxfile>")
        p = Path(path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(xml, encoding="utf-8")
        print("[flatdrawio] saved %s (%d cells)" % (p, self._id - 1))
