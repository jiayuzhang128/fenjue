"""Three reference templates in the flat pastel style: layered architecture, closed-loop flow, stage roadmap.

Run: python scripts/demo.py [output_dir] [--drawio]   (default: examples/ next to scripts/)
--drawio draws the same three figures through flatdrawio and writes editable .drawio files plus PNG previews.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

DRAWIO = "--drawio" in sys.argv
EXT = ".drawio" if DRAWIO else ".png"

if DRAWIO:
    from flatdrawio import (  # noqa: E402
        ACCENT, LOOP, MUTED, PALETTE, STAGE, bracket, box, canvas, diamond, junction, label_column, layer, line,
        note, path_arrow, rect, row_boxes, save, text,
    )
else:
    from flatfig import (  # noqa: E402
        ACCENT, LOOP, MUTED, PALETTE, STAGE, bracket, box, canvas, diamond, junction, label_column, layer, line,
        note, path_arrow, rect, row_boxes, save, text,
    )


def layered_architecture(out):
    """Layers as rows (label column + panel band), a side hub column, a cross-cutting band at the bottom."""
    fig, ax = canvas(2000, 1080)
    rect(ax, 1600, 20, 340, 820, PALETTE["purple"]["panel"])
    text(ax, 1770, 65, "智能中枢", size=18, color=LOOP)
    layers = [(80, "输入层", "blue", ["测试需求", "测试场景", "测试用例大纲"], "测试需求智能分析"),
              (350, "执行层", "green", ["测试脚本", "测试平台", "测试工具"], "测试脚本自动生成"),
              (620, "输出层", "yellow", ["过程日志", "测试结果", "测试报告"], "测试结果智能分析")]
    for y, name, family, items, hub in layers:
        label_column(ax, 30, y, 230, 220, name, PALETTE[family]["label"], size=20)
        rect(ax, 300, y, 1230, 220, PALETTE[family]["panel"])
        row_boxes(ax, 345, y + 60, 1140, 100, items, PALETTE[family]["box"], gap=60, size=16)
        box(ax, 1630, y + 60, 280, 100, hub, PALETTE["purple"]["box"], size=15)
        line(ax, [(1530, y + 110), (1630, y + 110)], color=ACCENT[family], lw=3)

    panel_x, panel_w = layer(ax, 890, 160, "贯穿机制", "gray", label_w=230, right=1940)
    row_boxes(ax, panel_x + 25, 925, panel_w - 50, 90, ["统一追溯", "配置基线", "任务状态", "质量门禁", "人工审核", "过程审计"],
              PALETTE["gray"]["box"], gap=24, size=15)
    return save(fig, out / ("template_layered_architecture" + EXT))


def closed_loop_flow(out):
    """Control-loop layout: input left, output right, main chain on one line, feedback below, human loop above."""
    fig, ax = canvas(2000, 720)
    cy = 370
    note(ax, 105, 300, "输入")
    note(ax, 1890, 300, "输出")
    box(ax, 20, 320, 170, 100, "经确认的\n测试用例大纲", PALETTE["blue"]["box"], size=11)
    junction(ax, 235, cy)
    box(ax, 300, 320, 230, 100, "智能中枢 / Agent\n理解意图 · 生成编排", PALETTE["purple"]["box"], size=11)
    box(ax, 590, 320, 260, 100, "脚本编制与生成工具\n规则校验 · 确定性生成", PALETTE["green"]["box"], size=11)
    rect(ax, 945, 250, 555, 220, PALETTE["yellow"]["panel"])
    text(ax, 960, 275, "测试脚本闭环验证", size=12, ha="left")
    box(ax, 960, 320, 200, 100, "平台执行\n归集证据", PALETTE["yellow"]["box"], size=14)
    diamond(ax, 1200, 295, 290, 150, "冒烟与有效性\n验证通过？", PALETTE["yellow"]["box"], size=10.5)
    box(ax, 1580, 320, 180, 100, "测试人员\n审核确认", PALETTE["green"]["label"], size=13)
    box(ax, 1800, 320, 180, 100, "正式\n测试脚本", PALETTE["green"]["box"], size=14)

    path_arrow(ax, [(190, cy), (211, cy)])
    path_arrow(ax, [(259, cy), (300, cy)])
    path_arrow(ax, [(530, cy), (590, cy)])
    path_arrow(ax, [(850, cy), (960, cy)])
    note(ax, 900, 345, "候选脚本", size=10)
    path_arrow(ax, [(1160, cy), (1200, cy)])
    path_arrow(ax, [(1490, cy), (1580, cy)])
    note(ax, 1535, 345, "是")
    path_arrow(ax, [(1760, cy), (1800, cy)])

    box(ax, 300, 130, 460, 90, "业务知识 · 平台规则 · 历史脚本\n测试数据 · 环境约束", PALETTE["gray"]["box"], size=13)
    path_arrow(ax, [(415, 220), (415, 320)])
    path_arrow(ax, [(660, 220), (660, 320)])
    path_arrow(ax, [(1670, 320), (1670, 90), (800, 90), (800, 320)], dashed=True, color=LOOP)
    note(ax, 1235, 66, "修改意见 · 人工微调")

    box(ax, 1230, 120, 230, 80, "人工接管\n问题确认与处置", PALETTE["pink"]["box"], size=12)
    path_arrow(ax, [(1345, 295), (1345, 200)])
    note(ax, 1333, 228, "停止条件：多轮迭代仍未通过", ha="right", size=10)

    box(ax, 600, 600, 400, 80, "脚本问题反馈\n证据 · 修改依据 · 前后轮对比", PALETTE["purple"]["label"], size=12)
    path_arrow(ax, [(1345, 445), (1345, 640), (1000, 640)], color=LOOP)
    note(ax, 1172, 616, "否 · 脚本问题", size=10)
    path_arrow(ax, [(600, 640), (235, 640), (235, 394)], color=LOOP)
    return save(fig, out / ("template_closed_loop_flow" + EXT))


def stage_roadmap(out):
    """Stages left to right (STAGE header + goal), outlined sub-steps below, bracket marking the current focus."""
    fig, ax = canvas(2000, 700)
    stages = [("第一阶段\n测试脚本自动生成", "提升脚本编制效率与规范性", ["图形化脚本编制工具建设", "智能生成能力接入", "执行验证与闭环完善"]),
              ("第二阶段\n测试结果智能分析", "提升失败定位与问题归因能力", ["测试脚本闭环验证", "正式测试结果智能分析"]),
              ("第三阶段\n测试需求智能分析", "提升场景设计与覆盖能力", ["需求结构化与方法基线", "智能场景生成", "覆盖追溯与反馈改进"]),
              ("第四阶段\n系统集成与闭环运行", "形成持续改进体系", ["测试资产贯通与统一基线", "流程编排与质量门禁", "闭环运行与持续改进"])]
    width = 430
    for i, ((title, goal, steps), (dark, light)) in enumerate(zip(stages, STAGE)):
        x = 50 + i * 490
        box(ax, x, 95, width, 95, title, dark, size=14)
        box(ax, x, 190, width, 70, goal, light, size=13, bold=False)
        if i:
            path_arrow(ax, [(x - 60, 142), (x, 142)])
        for j, step in enumerate(steps):
            y = 310 + j * 110
            box(ax, x, y, width, 80, step, "#FFFFFF", size=13, edge=dark)
            path_arrow(ax, [(x + width / 2, 260 if j == 0 else y - 30), (x + width / 2, y)], color=dark)

    bracket(ax, 50, 970, 65, "当前实施重点", color=LOOP)
    bracket(ax, 1030, 1950, 65, "后续实施方向", color=MUTED)
    path_arrow(ax, [(265, 610), (265, 660), (515, 660), (515, 350), (540, 350)], dashed=True, color=LOOP)
    note(ax, 392, 682, "配套实施")
    return save(fig, out / ("template_stage_roadmap" + EXT))


def main():
    args = [arg for arg in sys.argv[1:] if arg != "--drawio"]
    out = Path(args[0]) if args else Path(__file__).resolve().parent.parent / "examples"
    total = layered_architecture(out) + closed_loop_flow(out) + stage_roadmap(out)
    print(f"total lint warnings: {total}")


if __name__ == "__main__":
    main()
