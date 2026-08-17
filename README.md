# jiayu-skills

jiayu 的实用技能集，不绑定某个智能体，Claude Code、Codex、Cursor 等环境都可以用。

## 技能

| 技能 | 一句话 | 何时用 |
|---|---|---|
| [development-goal-execution](development-goal-execution/SKILL.md) | 六门流程：上下文恢复 → 第一性规划 → 第三方评审 → 规范化执行 → 全覆盖验收 → 对抗式审查。计划过别人的手，结论过敌人的眼 | 用户给出开发目标，或点名其中某一阶段；按点名的门做到停点 |

每个技能的完整说明看各自目录下的 SKILL.md。

## 安装

把需要的技能目录拷到对应环境的技能目录：

```bash
# Claude Code
cp -r <技能目录> ~/.claude/skills/

# Codex
cp -r <技能目录> ~/.codex/skills/

# Cursor
cp -r <技能目录> ~/.cursor/skills/
```

技能目录里的 `agents/openai.yaml` 只给 Codex 界面用，其他环境可以忽略。

## 仓库约定

- 技能正文用中文，贴合调用时的说法；`description` 里同时保留中文和英文触发词。
- 每个技能带 `evals/trigger-evals.json`：该触发和不该触发的真实说法各若干条，负例优先选和触发词沾边的近似场景，用于校验触发准确率。
- 不要把密钥、本机路径、某个环境专有的工具名写进技能正文。
