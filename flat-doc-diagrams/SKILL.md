---
name: flat-doc-diagrams
description: Use when drawing system architecture diagrams, layered or deployment diagrams, flowcharts, closed-loop process diagrams or stage roadmaps for technical documents, reports or slides (方案/需求文档配图、系统架构图、业务流程图、技术路线图、实施路径图), especially when figures must match an existing soft pastel flat-block style or when mermaid/default chart output looks unprofessional in Word.
version: 0.0.1
metadata:
  drawing-engines: [matplotlib-flatfig, drawio]
---

# Flat Pastel Document Diagrams

## Overview

Figures are drawn with matplotlib through `scripts/flatfig.py`: flat borderless pastel blocks, dark bold Microsoft YaHei text, thin dark orthogonal arrows on white. Every color family has three tints (label / panel / box) and each family carries one meaning, so a reader decodes every figure in a document the same way.

**Before drawing, Read the three PNGs in `examples/`** — they are the visual target. `scripts/demo.py` holds the code that produced them.

## Visual Grammar

| Element | Rule |
|---|---|
| Block | Flat rectangle, no border, shadow, rounded corner or gradient; text centered, bold, `#1F2937`; height ≥ 70 for one line, ≥ 100 (size 14) or ≥ 110 (size 16) for two lines |
| Layer / row | Left label column (`label` tint, size 18–20) + panel band to its right (`panel` tint) holding boxes (`box` tint); all boxes in a row share one height |
| Rows with different box counts | `row_boxes` stretches each row to the full panel width; if the text stresses columns, give every row one common box width and center the shorter rows |
| Group | `panel`-tint rectangle with a bold title at its top-left (size 12–16) |
| Flow connector | Horizontal/vertical runs only, `#374151`, width 2, filled head, starting and ending on box edge midpoints |
| Connector kinds | solid = main flow; dashed = optional, non-automated or human path; `both=True` = two-way link |
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

## draw.io Mode(for manual editing / 手动微调)

When the user wants to tweak the figure by hand afterwards, emit an editable **.drawio** file instead of (or alongside) the PNG. `scripts/flatdrawio.py` mirrors the flatfig API so both engines share one mental model:

```python
from flatdrawio import *
panel(290, 40, "#EEF7FB")                      # 内容面板(从层名列右侧 40px 起,勿压层名)
labelcol("接入层", 30, 40, "#BDE6F4")          # 左层名列(30..250)
box("模块文字<br>第二行", 330, 85, 493, 125, "#93D4EB")   # 值里直接写 <br>,生成器只转义一次
c1 = [box_id, ...]
edge(src, dst, exit=(0.5,1), entry=(0.5,0), points=[(1129,345),(715,345)])  # 显式锚点+路径点
save("arch.drawio", page_w=2000, page_h=1210)
```

**Hard-won pitfalls(每一条都踩过,违反必翻车):**

| # | 坑 | 规则 |
|---|---|---|
| 1 | `<br>` 被双重转义 → 图上显示字面 "<br>" | 值里写真实 `<br>`,写入 XML 前 **html.escape 恰好一次**(它会把 `<br>` 变 `&lt;br&gt;`,drawio 的 html=1 再渲染成换行) |
| 2 | 字体变 Helvetica 又细又丑 | 每个含文字的 style **必须显式 `fontFamily=Microsoft YaHei;fontStyle=1;`**(drawio 默认字体与 flat-doc 完全不同) |
| 3 | 字号比例失调 | drawio 没有 flatfig 的 ×1.6 内部缩放——**字号 = flatfig size × 1.6**(正文 15→24,层名 20→32,注释 12→19) |
| 4 | 层名压在内容面板上(层与内容连成一片) | 面板 x = 层名列 x + 220 + 40;**面板永远不碰层名列** |
| 5 | 边默认布线穿盒乱走 | 每条边必须给 `exitX/exitY + entryX/entryY` 锚点和 `<Array as="points">` 显式路径点;正交走向,先横后竖或先竖后横 |
| 6 | 虚线支撑线斜穿全图 | 逐条给单折路径点(出盒底 → 横移 → 入目标顶),横线走层间空隙 |
| 7 | 盲写 XML 直接交付 | **写完必须渲染预览自查**(同坐标 matplotlib 预览即可):无穿盒、无斜线、无字面 `<br>` 才准发 |

**Workflow(drawio)**: 生成 → draw.io 打开人工微调 → 用户导出 PNG(200%)→ 替换回文档。

## Workflow

1. Read `examples/*.png`. Pick the closest template in `scripts/demo.py` (layered architecture, closed-loop flow, stage roadmap) and copy its function as the starting point.
2. Copy `scripts/flatfig.py` into the project's figure directory, next to the figure script, so the figures stay reproducible without this skill.
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
| Drawing with mermaid, graphviz or draw.io defaults | Draw with `flatfig`; other tools do not reproduce this style |
| Borders, rounded corners, shadows, gradients, dark or saturated fills, white text on dark labels | Flat rectangles in the palette tints with dark text only |
| A different color per box ("rainbow") | Color by layer order or by the meaning column |
| Sentences inside boxes | Shorten to a noun phrase; the shrink warning flags it |
| Diagonal or curved connectors, arrows cutting through boxes | Route with horizontal/vertical runs around blocks |
| One long single-row chain (4:1 canvas) | Wrap into two rows or turn the tail down; the aspect warning flags it |
| Canvas width other than 2000, or inserting narrower than ~14 cm | Keep width 2000 and insert at full text width; split a crowded figure instead of shrinking it |
| Declaring the figure done without viewing it | Lint 0 is necessary but not sufficient; always Read the PNG |
