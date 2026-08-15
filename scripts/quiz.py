#!/usr/bin/env python3
"""从知识库题库抽题自测，或从外部真题源抽考研真题。

用法:
    python3 scripts/quiz.py                    # 全部章节随机 5 题
    python3 scripts/quiz.py -c 极限 -n 3       # 指定章节 3 题
    python3 scripts/quiz.py --answer           # 同时显示答案(自测完再看)
    python3 scripts/quiz.py --zhenti 2024      # 2024 数一真题随机 5 题
    python3 scripts/quiz.py --zhenti 2024 --q 1,17,3  # 指定题号

知识库题库格式: knowledge/*.md 中 `## 题库` 区段下的行:
    - Q. <题目> :: <答案/提示>
真题源: 先运行 scripts/setup-sources.sh 拉取(本地 sources/, 不入库)。
"""
from __future__ import annotations

import argparse
import pathlib
import random
import re

ROOT = pathlib.Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = ROOT / "knowledge"
SOURCES_DIR = ROOT / "sources"
Q_RE = re.compile(r"^-\s*Q\.\s*(.+?)\s*::\s*(.+)$", re.M)
# 真题解析文件按【N】分题(OCR 残渣可能粘在标记前, 故不锚定行首),【答案】单独成行
ZHENTI_Q_RE = re.compile(r"【(\d{1,2})】")
SECTION_OF = lambda n: "选择" if n <= 10 else ("填空" if n <= 16 else "解答")


def load_bank(chapter: str | None) -> list[tuple[str, str, str]]:
    bank = []
    for p in sorted(KNOWLEDGE_DIR.glob("*.md")):
        if p.name.startswith("_") or p.name == "syllabus.md":
            continue
        title = p.read_text(encoding="utf-8").splitlines()[0].lstrip("# ").strip()
        if chapter and chapter not in title and chapter not in p.stem:
            continue
        for q, a in Q_RE.findall(p.read_text(encoding="utf-8")):
            bank.append((title, q.strip(), a.strip()))
    return bank


def parse_zhenti(year: str) -> dict[int, dict]:
    """解析 sources 真题 -> {题号: {"stem","answer","solution"}}。

    真题源有两种格式:
    - 新版(约2015+): solutions/<年>年解析/<年>.md 内【N】题干+【答案】, 无解题过程
    - 旧版: 题干在 papers/<年>真题.md 的 (N) 行, solutions 内 (N)【答案】+【解】完整过程
    """
    repo = SOURCES_DIR / "Kaoyan-Math1-Papers"
    sol_files = sorted((repo / "solutions").glob(f"{year}*/{year}*.md"))
    if not sol_files:
        raise SystemExit(
            f"找不到 {year} 年真题解析。请先运行: bash scripts/setup-sources.sh\n"
            f"(sources/Kaoyan-Math1-Papers/solutions/{year}年解析/)")
    text = sol_files[0].read_text(encoding="utf-8")

    questions: dict[int, dict] = {}

    # ── 新版格式: 【N】题干 ... 【答案】x ──
    num, stem, ans, in_ans = None, [], [], False
    for line in text.splitlines():
        if line.startswith("#"):
            continue
        m = ZHENTI_Q_RE.search(line)
        if m:
            if num is not None:
                questions[num] = {"stem": "\n".join(stem).strip(),
                                  "answer": "\n".join(ans).strip(), "solution": ""}
            suffix = line[m.end():].strip()
            num, stem, ans, in_ans = int(m.group(1)), ([suffix] if suffix else []), [], False
        elif line.startswith("【答案】"):
            in_ans = True
            ans.append(line[len("【答案】"):].strip())
        elif num is not None:
            (ans if in_ans else stem).append(line)
    if num is not None:
        questions[num] = {"stem": "\n".join(stem).strip(),
                          "answer": "\n".join(ans).strip(), "solution": ""}

    # ── 旧版格式: 解析文件以 (N)【答案】 开头 + papers 文件含题干 ──
    if len(questions) < 10:
        questions.clear()

        def _set(n: int, a: str, s: list) -> None:
            q = questions.setdefault(n, {"stem": "", "answer": "", "solution": ""})
            q["answer"], q["solution"] = a, "\n".join(s).strip()

        # 答案+过程        num, ans, sol = None, "", []
        for line in text.splitlines():
            m = re.match(r"^[(（](\d{1,2})[)）]【答案】\s*(.*)$", line)
            if m:
                if num is not None:
                    _set(num, ans, sol)
                num, ans, sol = int(m.group(1)), m.group(2).strip(), []
            elif num is not None:
                sol.append(line)
        if num is not None:
            _set(num, ans, sol)
        # 题干(来自 papers/)
        paper = sorted((repo / "papers").glob(f"{year}*真题*.md"))
        if not paper:
            raise SystemExit(f"{year} 年解析为旧版格式, 但 papers/ 下找不到题干文件。")
        num, stem = None, []
        for line in paper[0].read_text(encoding="utf-8").splitlines():
            if line.startswith("#"):
                continue
            m = re.match(r"^[(（](\d{1,2})[)）]\s*(.*)$", line)
            if m:
                if num is not None:
                    questions.setdefault(num, {"stem": "", "answer": "", "solution": ""})["stem"] = \
                        "\n".join(stem).strip()
                num, stem = int(m.group(1)), [m.group(2)]
            elif num is not None:
                stem.append(line)
        if num is not None:
            questions.setdefault(num, {"stem": "", "answer": "", "solution": ""})["stem"] = \
                "\n".join(stem).strip()
        for n, q in questions.items():
            if not q["stem"]:
                q["stem"] = "(题干缺失, 请读原文件)"
    return questions


def main() -> None:
    ap = argparse.ArgumentParser(description="知识库/真题抽题自测")
    ap.add_argument("-c", "--chapter", help="章节关键词(标题或文件名匹配), 如: 极限")
    ap.add_argument("-n", "--num", type=int, default=5, help="抽题数量")
    ap.add_argument("--answer", action="store_true", help="同时显示答案")
    ap.add_argument("--zhenti", metavar="YEAR", help="从真题源抽题, 如: --zhenti 2024")
    ap.add_argument("--q", help="指定真题题号(逗号分隔), 如: --q 1,17")
    args = ap.parse_args()

    if args.zhenti:
        questions = parse_zhenti(args.zhenti)
        if not questions:
            raise SystemExit(f"{args.zhenti} 年解析文件解析不到题目, 请检查文件格式。")
        if len(questions) < 10:
            print(f"⚠ 该年份解析文件格式不规则(仅解析到 {len(questions)} 题, 老年份存在分节重新编号等), "
                  f"建议直接阅读 sources/Kaoyan-Math1-Papers/ 下对应年份的原文。\n")
        if args.q:
            nums = [int(x) for x in args.q.split(",") if x.strip().isdigit()]
        else:
            nums = random.sample(sorted(questions), min(args.num, len(questions)))
        print(f"{args.zhenti} 年数学一真题, 共 {len(questions)} 题, 本次: {nums}\n")
        for n in nums:
            q = questions[n]
            print(f"【{n}】({SECTION_OF(n)}题)\n{q['stem']}")
            if args.answer:
                print(f"  参考答案: {q['answer'] or '(未提供, 需自行推导)'}")
                if q["solution"]:
                    print(f"  解析: {q['solution']}")
                print()
            else:
                print()
        if not args.answer:
            print("做完后加 --answer 查看; 注意解析源可能有 OCR 噪声, 以推导为准。")
        return

    bank = load_bank(args.chapter)
    if not bank:
        print("题库为空或未匹配到章节。请在 knowledge/<章节>.md 的 `## 题库` 区段"
              "按 `- Q. 题目 :: 答案` 格式补充。")
        return
    picks = random.sample(bank, min(args.num, len(bank)))
    print(f"本章匹配题量 {len(bank)}, 抽取 {len(picks)} 题:\n")
    for i, (title, q, a) in enumerate(picks, 1):
        print(f"[{i}] ({title})\n    {q}")
        if args.answer:
            print(f"    答案/提示: {a}\n")
    if not args.answer:
        print("\n做完后用 --answer 查看答案; 错题按 mistakes/_TEMPLATE.md 记入错题本。")


if __name__ == "__main__":
    main()
