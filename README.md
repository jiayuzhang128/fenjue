# jiayu-skills

jiayu 的实用技能。写成不绑定某个智能体的流程，能读仓库、改文件、跑检查的环境都可以用。

这些技能用更多 token，换更少后期返工。这笔开销是故意的。

## 技能

| 技能 | 何时用 |
|---|---|
| [development-goal-execution](development-goal-execution/SKILL.md) | 用户给出开发目标，或点名其中某一阶段；按点名的门做到停点，提高一次做对的概率 |

## 安装

把技能目录拷到对应环境的技能目录：

```bash
# Claude Code
cp -r development-goal-execution ~/.claude/skills/

# Codex
cp -r development-goal-execution ~/.codex/skills/
```

`agents/openai.yaml` 只给 Codex 界面用，其他环境可以忽略。

## 约定

- 技能正文用中文，贴合调用时的说法。
- `description` 里保留会触发的中文阶段名。
- 不要把密钥、本机路径、某个环境专有的工具名写进技能正文。
