---
name: flat-doc-diagrams
description: Use when drawing system architecture diagrams, layered or deployment diagrams, flowcharts, closed-loop process diagrams or stage roadmaps for technical documents, reports or slides (方案/需求文档配图、系统架构图、业务流程图、技术路线图、实施路径图), especially when figures must match an existing soft pastel flat-block style, when mermaid/default chart output looks unprofessional in Word, or when the figure must stay editable by hand as a .drawio source file (可编辑源文件、手动微调、draw.io).
version: 0.0.2
metadata:
  drawing-engines: [matplotlib-flatfig, drawio]
---

# Flat Pastel Document Diagrams

## Overview

Figures are drawn with matplotlib through `scripts/flatfig.py` (PNG) or, when the user wants to adjust them by hand, through `scripts/flatdrawio.py` (editable .drawio plus a PNG preview). Both take the same calls and produce the same look: flat borderless pastel blocks, dark bold Microsoft YaHei text, thin dark orthogonal arrows on white. Every color family has three tints (label / panel / box) and each family carries one meaning, so a reader decodes every figure in a document the same way.

**Before drawing, Read the three PNGs in `examples/`** — they are the visual target. `scripts/demo.py` holds the code that produced them.

## Visual Grammar

| Element | Rule |
|---|---|
| Block | Flat rectangle, no border, shadow, rounded corner or gradient; text centered, bold, `#1F2937`; height ≥ 70 for one line, ≥ 100 (size 14) or ≥ 110 (size 16) for two lines |
| Layer / row | Left label column (`label` tint, size 18–20) + panel band to its right (`panel` tint) holding boxes (`box` tint); all boxes in a row share one height |
| Rows with different box counts | `row_boxes` stretches each row to the full panel width; if the text stresses columns, give every row one common box width and center the shorter rows |
| Group | `panel`-tint rectangle with a bold title at its top-left (size 12–16) |
| Flow connector | Horizontal/vertical runs only, `#374151`, width 2, filled head, starting and ending on box edge midpoints |
| Connector kinds | solid = main flow; dashed = optional, non-automated or human path; `both=True` = two-way link with a head at each end of the path |
| Return path | Color the whole path that leads back to an earlier step `LOOP` purple, starting with the edge that leaves the main chain (e.g. the 否 edge of a decision) |
| Association | Layer ↔ side hub: plain `ACCENT[family]` line, width 3, no head ("serves / is supported by"). Add dark arrows between layers only when the text describes data flowing between them |
| Edge label | `note()`, regular gray `#4B5563`. Horizontal line: label centered about 22 units above it. Vertical line: `ha="left"` at x + 12 or `ha="right"` at x − 12 |
| Decision | `diamond()` in yellow `box` tint, same font size as neighbouring boxes; make it 1.8× the width and 2× the height of a box holding the same text; label branches 是/否 |
| Control loop | For generate–verify–correct loops: input left, output right, main chain on one horizontal line, automatic feedback below in `LOOP`, human outer loop dashed above. Use `junction()` ⊗ only where fed-back corrections merge with the original input; feedback that changes a step's rules or configuration points straight into that step |
| Process with branches | Main chain on the top row, exception/return branch on a row below; when the tail is long, turn it down at the right end instead of stretching the row |
| Stage sequence | `STAGE` pairs (dark header + light goal row) left to right; sub-steps as white boxes outlined in the stage color (`box(..., "#FFFFFF", edge=dark)`), top-aligned; shorter stages leave space below |
| Emphasis | `bracket()` over grouped stages or boxes, label size 14–16 (e.g. 当前实施重点 in `LOOP`, 后续方向 in `MUTED`) |

## Color Semantics

| Family | label | panel | box | Meaning |
|---|---|---|---|---|
| blue | `#BDE6F4` | `#EEF7FB` | `#93D4EB` | input: requirements, test cases, data sources, sensing/field data |
| green | `#D8EBC5` | `#F3F8EE` | `#ADD98E` | processing and execution: tools, platforms, scripts; green **label** tint = human review/approval node |
| yellow | `#FFE19F` | `#FFF8E5` | `#FFCA58` | output: applications, results, evidence, verification, decisions |
| purple | `#E4D5F2` | `#F6F0FB` | `#CEB4E6` | AI / Agent / model hub, feedback |
| gray | `#CDD9E7` | `#F2F5F8` | `#DDE5EE` | infrastructure, knowledge, environment, cross-cutting mechanisms, existing systems |
| pink | `#F5CBD5` | `#FCEFF2` | `#F2B8C6` | devices under test, exceptions, manual takeover, false alarms, defects, risks |

- **Layered architecture:** stacked layers take blue → green → yellow in flow order (source/input → processing → application/output); side hub = purple; cross-cutting band at the bottom = gray. Order layers top to bottom in flow order as in the template, unless the document's domain draws them bottom-up (e.g. 感知层 at the bottom); then keep the same color order by flow.
- **Flow figures:** color each node by the meaning column. When two meanings fit, choose the one that differs from its neighbours, and give the same node type the same color in every figure of the document.
- **Stages:** `STAGE` colors mark sequence position only. Beyond four stages, continue with the `label`/`panel` tints of purple, then gray.
- **Lines:** `LOOP #5B3A8C` (return paths, highlight titles), `MUTED #6B7280` (secondary brackets), `ACCENT[family]` (association lines, defined for all six families).

## Editable draw.io Output

When the user wants to adjust the figure by hand afterwards (可编辑、手动微调、要 .drawio 源文件), draw it through `scripts/flatdrawio.py`. It has the same functions and signatures as flatfig, so the Workflow below applies unchanged apart from these points:

1. Copy both `flatfig.py` and `flatdrawio.py` next to the figure script, import from `flatdrawio`, and save to a `.drawio` path: `save(fig, "image/图1_示例.drawio")`.
2. `save()` runs the same lint and writes `图1_示例_preview.png` beside the `.drawio` file. Fix the layout to 0 lint warnings and Read the preview as in Workflow step 6; it shows the same shapes at the same coordinates as the `.drawio` file.
3. When the target `.drawio` already exists with different content, `save()` first renames it to `<name>.bak-<timestamp>`. Regenerating rebuilds the figure from the script and drops edits made in draw.io, so before regenerating a file the user may have edited, tell them their version is kept in that backup. Backups created by your own reruns while fixing lint, before the user has received the file, can be deleted.
4. The user edits in draw.io and exports the final PNG there (or `draw.io -x -f png -s 2 -b 20 -o 图1.png 图1.drawio` with draw.io desktop installed). That export, not the preview, goes into the document. draw.io crops the export to the drawn content, so the canvas margins are replaced by the `-b` border.

Text is plain text in both engines: break lines with `
`, and characters such as `&` or `<` appear literally. A connector end placed on the border of a box, diamond or junction is attached to that shape and follows it when the user moves it; an end in open space stays a free point. The file names Microsoft YaHei; on a machine without it draw.io substitutes its default font.

`python scripts/demo.py --drawio` regenerates the three `examples/*.drawio` templates.

## Workflow

1. Read `examples/*.png`. Pick the closest template in `scripts/demo.py` (layered architecture, closed-loop flow, stage roadmap) and copy its function as the starting point.
2. Copy `scripts/flatfig.py` (and `scripts/flatdrawio.py` for editable output) into the project's figure directory, next to the figure script, so the figures stay reproducible without this skill.
3. Canvas width is **always 2000**; height fits content, and width/height must stay ≤ 3.2. Use explicit coordinates:
   - horizontal gaps between neighbouring boxes 30–60;
   - vertical gaps between rows 50–150;
   - margins ≥ 20, measured from the outermost drawn element (bracket labels included) and equal left/right and top/bottom.
4. Box text: at most 2 lines, about 12 Chinese characters per line, short items joined with ` · `. Details belong in the document text, not in the figure. Sizes:
   - layer labels 18–20, box text 14–16 (13 minimum), notes 11–12 (10 minimum ≈ 4.9 pt printed);
   - figures with ≤ 8 boxes may go up to 18 for box text and 14 for notes.
5. Run the script. `save()` prints `[flatfig]` warnings: text shrunk below 95%, diagonal connector, connector through a box, overlapping boxes, clipped text, label on a line or box, canvas too flat. Fix the layout until it reports **0 lint warnings**.
6. Read the saved PNG. Check:
   - arrows touch box edges;
   - nothing crosses a box;
   - every label sits beside its own line;
   - colors follow the semantics rules;
   - rows and columns align;
   - the composition is balanced, with no empty quadrant; move a branch into the gap or wrap the chain.
7. Insert at full text width, e.g. python-docx `add_picture(path, width=Cm(15.4))`. Printed size ≈ `size × 1.6 × insert_cm / 50.8` pt, which is ≈ 0.485 × size at 15.4 cm.

## Minimal Example

```python
from flatfig import *   # flatfig.py copied next to this script (Workflow step 2)

fig, ax = canvas(2000, 630)
for y, name, family, items in ((40, "执行层", "green", ["测试脚本", "测试平台", "测试工具"]),
                               (240, "输出层", "yellow", ["过程日志", "测试结果", "测试报告"])):
    px, pw = layer(ax, y, 160, name, family)
    row_boxes(ax, px + 40, y + 30, pw - 80, 100, items, PALETTE[family]["box"], gap=60, size=16)
box(ax, 500, 480, 300, 100, "结果分析", PALETTE["yellow"]["box"])
box(ax, 1200, 480, 300, 100, "人工确认", PALETTE["green"]["label"])
path_arrow(ax, [(800, 530), (1200, 530)])
note(ax, 1000, 508, "分析建议")
save(fig, "image/图1_示例.png")   # must report 0 lint warnings
```

Requires Python 3 and matplotlib. The CJK font is auto-detected (Microsoft YaHei, PingFang, Noto Sans CJK); on `FileNotFoundError`, install Noto Sans CJK.

## Common Mistakes

| Mistake | Fix |
|---|---|
| Drawing with mermaid, graphviz, draw.io's default shapes or hand-written draw.io XML | Draw with `flatfig`, or `flatdrawio` for an editable file; other routes do not reproduce this style |
| Borders, rounded corners, shadows, gradients, dark or saturated fills, white text on dark labels | Flat rectangles in the palette tints with dark text only |
| A different color per box ("rainbow") | Color by layer order or by the meaning column |
| Sentences inside boxes | Shorten to a noun phrase; the shrink warning flags it |
| Diagonal or curved connectors, arrows cutting through boxes | Route with horizontal/vertical runs around blocks |
| One long single-row chain (4:1 canvas) | Wrap into two rows or turn the tail down; the aspect warning flags it |
| Canvas width other than 2000, or inserting narrower than ~14 cm | Keep width 2000 and insert at full text width; split a crowded figure instead of shrinking it |
| Declaring the figure done without viewing it | Lint 0 is necessary but not sufficient; always Read the PNG |
