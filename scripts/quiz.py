#!/usr/bin/env python3
"""从知识库题库抽题自测。

用法:
    python3 scripts/quiz.py                    # 全部章节随机 5 题
    python3 scripts/quiz.py -c 极限 -n 3       # 指定章节 3 题
    python3 scripts/quiz.py --answer           # 同时显示答案(自测完再看)

题库格式: knowledge/*.md 中 `## 题库` 区段下的行:
    - Q. <题目> :: <答案/提示>
"""
from __future__ import annotations

import argparse
import pathlib
import random
import re

KNOWLEDGE_DIR = pathlib.Path(__file__).resolve().parent.parent / "knowledge"
Q_RE = re.compile(r"^-\s*Q\.\s*(.+?)\s*::\s*(.+)$", re.M)


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


def main() -> None:
    ap = argparse.ArgumentParser(description="知识库抽题自测")
    ap.add_argument("-c", "--chapter", help="章节关键词(标题或文件名匹配), 如: 极限")
    ap.add_argument("-n", "--num", type=int, default=5, help="抽题数量")
    ap.add_argument("--answer", action="store_true", help="同时显示答案")
    args = ap.parse_args()

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
