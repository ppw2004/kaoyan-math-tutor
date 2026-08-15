#!/usr/bin/env bash
# 拉取外部真题源到 sources/（不入库，仅本地使用）。
# 只保留 .md 文件（稀疏检出），避免 ~185MB 的图片/JSON 一起下来。
#
# 用法: bash scripts/setup-sources.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCES="$ROOT/sources"
mkdir -p "$SOURCES"

# ── 源 1: 考研数学一真题库 1987-2025 (CC BY-NC-SA 4.0, Nebutra) ──
NAME="Kaoyan-Math1-Papers"
URL="https://github.com/TsekaLuk/Kaoyan-Math1-Papers.git"
DEST="$SOURCES/$NAME"

if [ -d "$DEST/.git" ]; then
    echo "✓ $NAME 已存在, 更新中..."
    git -C "$DEST" pull --ff-only 2>/dev/null || echo "  (更新失败, 保留本地版本)"
else
    echo "→ 克隆 $NAME (仅 .md, 需要网络)..."
    git clone --depth 1 --filter=blob:none --sparse "$URL" "$DEST"
    git -C "$DEST" sparse-checkout set --no-cone '**.md'
    echo "✓ 完成: $DEST"
fi

# ── 署名与许可说明 ──
cat > "$SOURCES/SOURCES.md" <<'EOF'
# 外部数据源说明（本地目录，不入库）

| 目录 | 内容 | 许可证 | 仓库 |
|------|------|--------|------|
| Kaoyan-Math1-Papers/ | 数学一 1987-2025 真题+解析 (Markdown) | CC BY-NC-SA 4.0 | github.com/TsekaLuk/Kaoyan-Math1-Papers |

以上内容由各自作者持有版权，仅限个人非商业学习使用；
本仓库不收录、不分发这些内容，仅提供索引与本地拉取工具。
EOF

echo ""
echo "全部源就绪。抽真题: python3 scripts/quiz.py --zhenti 2024"
