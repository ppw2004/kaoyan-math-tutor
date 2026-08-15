# kaoyan-math-tutor

考研高等数学「良师益友」型 Claude Skill：苏格拉底式引导教学 + 考纲知识库 + 错题本 + 艾宾浩斯间隔复习。

## 安装

```bash
# 作为 Claude Code 个人技能安装(全局)
git clone https://github.com/ppw2004/kaoyan-math-tutor.git ~/.claude/skills/kaoyan-math-tutor

# 可选: 拉取外部数据源(数一真题1987-2025 + GPL讲法参考笔记, 本地 sources/ 不入库, ~7MB)
cd ~/.claude/skills/kaoyan-math-tutor && bash scripts/setup-sources.sh
```

安装后在本仓库目录（或含本 skill 的项目）里对 Claude 说「开始学极限」「这道题不会」「看看我的进度」「今天该复习什么」「做两道 2024 真题」即可。

> 学习数据（progress.md / mistakes/）直接写在本仓库内，跟着 git 走，换机器 clone 即同步。

## 版权说明

本仓库全部原创内容（讲义骨架、脚本），MIT 协议。**不收录任何真题或第三方讲义**，外部参考均通过 `setup-sources.sh` 拉取到本地 `sources/`（已 gitignore）：

- [TsekaLuk/Kaoyan-Math1-Papers](https://github.com/TsekaLuk/Kaoyan-Math1-Papers)（CC BY-NC-SA 4.0）— 真题练习用
- [BlandAlpha/obsidian_math](https://github.com/BlandAlpha/obsidian_math)（GPL-3.0）— 讲法参考用，只读不抄，讲义均为自写

考纲动词层级（了解/理解/会/掌握）为对官方《数学考试大纲》的事实性转述，大纲原文版权归考试中心。

## 目录结构

```
kaoyan-math-tutor/
├── SKILL.md              # 技能入口：教学人设、工作流、文件约定
├── knowledge/
│   ├── syllabus.md       # 考纲知识树（章节/先修关系/数一二三适用范围）
│   ├── _TEMPLATE.md      # 章节知识库模板
│   └── jiuxian.md        # 示例章节：函数、极限、连续
├── mistakes/
│   └── _TEMPLATE.md      # 错题记录模板（frontmatter 由脚本解析）
├── progress.md           # 学习进度 + 学习日志
└── scripts/
    ├── review.py         # 错题间隔复习调度（到期提醒 / 答对升级 / 答错重置）
    ├── quiz.py           # 知识库/真题抽题自测（--zhenti 2024 --q 1,17 --answer）
    └── setup-sources.sh  # 稀疏克隆外部源到 sources/（真题库 + 讲法参考，仅 .md，~7MB）
```

## 使用

| 你说 | Claude 做 |
|------|-----------|
| 「开始学 <章节>」 | 检查先修章节掌握度 → 按知识库结构讲解 → 出检验题 → 更新 progress.md |
| 「这道题不会：<题>」 | 三层提示链引导（方向→关键步→完整解），确认真懂 |
| 「记错题」 | 按 mistakes 模板记录错因与关键步 |
| 「今天该复习什么」 | 运行 review.py 列出到期错题，先重做后讲评 |
| 「看看我的进度」 | 渲染 progress.md + 错题趋势 |

## 间隔复习规则

- 答对：间隔 1→2→4→7→15→30 天逐级上升，到 30 天视为掌握（mastered）
- 答错：间隔重置为 1 天，累计错次 +1

## 状态

- [x] 骨架：SKILL.md / 知识树 / 模板 / 调度与抽题脚本
- [ ] 知识库：9 章内容（欢迎 PR 或让 Claude 按模板逐章生成）
- [ ] 题库扩充：历年真题按考点打标入库
- [ ] 线代 / 概率论分册

## License

MIT
