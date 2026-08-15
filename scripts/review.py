#!/usr/bin/env python3
"""错题间隔复习调度器（艾宾浩斯）。

用法:
    python3 scripts/review.py                    # 列出今天到期的错题
    python3 scripts/review.py --all              # 列出全部错题概览
    python3 scripts/review.py --done <文件名>    # 某题答对: 间隔翻倍
    python3 scripts/review.py --fail <文件名>    # 某题答错: 间隔重置为1天

错题文件为 mistakes/*.md, 依靠 YAML frontmatter 中的
interval_days / next_review / wrong_count / status 字段调度。
无第三方依赖。
"""
from __future__ import annotations

import argparse
import datetime as dt
import pathlib
import re
import sys

MISTAKES_DIR = pathlib.Path(__file__).resolve().parent.parent / "mistakes"
INTERVAL_LADDER = [1, 2, 4, 7, 15, 30]  # 天; 30 封顶, 连续达标视为掌握
MASTER_THRESHOLD = 30  # 间隔达到该值后标记 mastered


def parse_frontmatter(path: pathlib.Path) -> dict:
    """极简 frontmatter 解析, 只支持 key: value 与 key: [a, b] 两种行。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", text, re.S)
    if not m:
        raise ValueError(f"{path.name}: 缺少 frontmatter")
    meta = {}
    for line in m.group(1).splitlines():
        kv = re.match(r"^(\w+):\s*(.+)$", line.strip())
        if not kv:
            continue
        key, raw = kv.groups()
        raw = raw.strip()
        if raw.startswith("[") and raw.endswith("]"):
            meta[key] = [t.strip() for t in raw[1:-1].split(",") if t.strip()]
        elif re.fullmatch(r"\d{4}-\d{2}-\d{2}", raw):
            meta[key] = dt.date.fromisoformat(raw)
        elif raw.isdigit():
            meta[key] = int(raw)
        else:
            meta[key] = raw.strip("\"'")
    return meta


def write_field(path: pathlib.Path, key: str, value) -> None:
    """把 frontmatter 中的单行字段替换为新值, 其余原样保留。"""
    text = path.read_text(encoding="utf-8")
    m = re.match(r"^(---\n)(.*?)(\n---)", text, re.S)
    body = m.group(2)
    new_body, n = re.subn(
        rf"^(\s*{key}:).*$", rf"\1 {value}", body, count=1, flags=re.M
    )
    if n == 0:
        new_body = body + f"\n{key}: {value}"
    path.write_text(text[: m.start(2)] + new_body + text[m.end(2):], encoding="utf-8")


def load_mistakes(active_only: bool = True) -> list[tuple[pathlib.Path, dict]]:
    items = []
    for p in sorted(MISTAKES_DIR.glob("*.md")):
        if p.name.startswith("_"):
            continue
        meta = parse_frontmatter(p)
        if active_only and meta.get("status") == "archived":
            continue
        items.append((p, meta))
    return items


def next_interval(current: int) -> int:
    for step in INTERVAL_LADDER:
        if step > current:
            return step
    return INTERVAL_LADDER[-1]


def mark(path_name: str, ok: bool) -> None:
    matches = [p for p in MISTAKES_DIR.glob("*.md")
               if p.name.startswith(path_name) or path_name == p.stem]
    if not matches:
        sys.exit(f"找不到错题文件: {path_name}")
    path = matches[0]
    meta = parse_frontmatter(path)
    today = dt.date.today()
    if ok:
        interval = next_interval(int(meta.get("interval_days", 1)))
        status = "mastered" if interval >= MASTER_THRESHOLD else meta.get("status", "active")
    else:
        interval = 1
        status = "active"
        write_field(path, "wrong_count", int(meta.get("wrong_count", 0)) + 1)
    write_field(path, "interval_days", interval)
    write_field(path, "next_review", (today + dt.timedelta(days=interval)).isoformat())
    if status != meta.get("status"):
        write_field(path, "status", status)
    print(f"✓ {path.name}: 下次复习 {(today + dt.timedelta(days=interval)).isoformat()} "
          f"(间隔 {interval} 天, 状态 {status})")


def main() -> None:
    ap = argparse.ArgumentParser(description="错题间隔复习调度")
    ap.add_argument("--all", action="store_true", help="列出全部错题")
    ap.add_argument("--done", metavar="FILE", help="标记答对(间隔翻倍)")
    ap.add_argument("--fail", metavar="FILE", help="标记答错(间隔重置)")
    args = ap.parse_args()

    if args.done:
        mark(args.done, ok=True)
        return
    if args.fail:
        mark(args.fail, ok=False)
        return

    today = dt.date.today()
    items = load_mistakes(active_only=not args.all)
    due = [(p, m) for p, m in items if m.get("status") != "mastered"
           and m.get("next_review", today) <= today]
    if not items:
        print("错题本为空。学习时遇到错题按 mistakes/_TEMPLATE.md 记录。")
        return
    if due:
        print(f"今日到期错题 {len(due)} 道:")
        for p, m in due:
            print(f"  - {p.name}  [{m.get('chapter')}/{m.get('topic')}] "
                  f"错 {m.get('wrong_count', 1)} 次")
    else:
        upcoming = min(items, key=lambda pm: pm[1].get("next_review", today))
        print(f"今日无到期错题。最早下次复习: "
              f"{upcoming[1].get('next_review')} ({upcoming[0].name})")
    active = [m for _, m in items if m.get("status") == "active"]
    mastered = [m for _, m in items if m.get("status") == "mastered"]
    print(f"统计: active {len(active)} / mastered {len(mastered)} / 共 {len(items)}")


if __name__ == "__main__":
    main()
