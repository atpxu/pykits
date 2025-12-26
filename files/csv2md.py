import csv
import sys


def escape_cell(s: str) -> str:
    if s is None:
        return ""

    # 统一换行：CSV 单元格里的多行 → <br>
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.replace("\n", "<br>")

    # 去掉首尾多余空白（保留内容）
    s = s.strip()

    # 防 CSV / 表格软件公式解析（= + - @）
    if s[:1] in ("=", "+", "-", "@"):
        s = " " + s

    # Markdown 表格分隔符转义
    s = s.replace("|", "\\|")

    return s


csv_path = sys.argv[1]

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.reader(f)
    rows = list(reader)

if not rows:
    sys.exit(0)

header = rows[0]
body = rows[1:]

# 表头
print("| " + " | ".join(escape_cell(x) for x in header) + " |")
print("| " + " | ".join("---" for _ in header) + " |")

# 表体
for r in body:
    r = r + [""] * (len(header) - len(r))
    print("| " + " | ".join(escape_cell(x) for x in r[:len(header)]) + " |")
