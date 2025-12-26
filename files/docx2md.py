#!/usr/bin/env python3
import argparse
import shutil
import subprocess
import sys
from pathlib import Path


def which_or_exit(cmd: str) -> None:
    if shutil.which(cmd) is None:
        print(f"❌ {cmd} not found. Please install it first.", file=sys.stderr)
        sys.exit(1)


def run_pandoc(abs_docx: Path, output_dir: Path) -> None:
    base = abs_docx.stem
    out_md = output_dir / f"{base}.md"
    media_dir_name = f"{base}_images"  # 注意：相对于 output_dir
    media_dir = output_dir / media_dir_name

    media_dir.mkdir(parents=True, exist_ok=True)

    # 关键点：
    # - cwd=output_dir：让 pandoc 写出的图片引用路径相对于输出 md（Joplin 友好）
    # - abs_docx：避免 cwd 改变后输入路径失效
    cmd = [
        "pandoc",
        str(abs_docx),
        "-o",
        str(out_md.name),  # 在 output_dir 里写
        "--extract-media",
        media_dir_name,  # 相对于 output_dir
        "-t",
        "gfm",  # 去掉 {width=...} 这类 pandoc 扩展，Joplin 更兼容
        "--wrap=none",
    ]

    print(f"➡️  Converting: {abs_docx} -> {out_md}")
    subprocess.run(cmd, cwd=str(output_dir), check=True)
    print(f"✅  Output: {out_md}")


def collect_docx_inputs(input_path: Path) -> list[Path]:
    if input_path.is_file():
        if input_path.suffix.lower() != ".docx":
            print("❌ Input file must be .docx", file=sys.stderr)
            sys.exit(1)
        return [input_path]

    if input_path.is_dir():
        files = sorted(input_path.glob("*.docx"))
        return files

    print(f"❌ Input not found: {input_path}", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="docx2md",
        description="Convert a .docx file or a directory of .docx files to Markdown, "
                    "extracting images (Joplin-friendly).",
    )
    parser.add_argument(
        "input",
        help="Input .docx file or directory containing .docx files",
    )
    parser.add_argument(
        "-o",
        "--output",
        default="./output",
        help='Output directory (default: "./output")',
    )

    args = parser.parse_args()

    which_or_exit("pandoc")

    input_path = Path(args.input).expanduser()
    output_dir = Path(args.output).expanduser()
    output_dir.mkdir(parents=True, exist_ok=True)

    docx_files = collect_docx_inputs(input_path)
    if not docx_files:
        print("⚠️  No .docx files found.")
        return

    # 绝对路径：避免 cwd=output_dir 后路径失效
    for f in docx_files:
        abs_docx = f.resolve()
        run_pandoc(abs_docx, output_dir)

    print(f"🎉 Done. Output directory: {output_dir}")


if __name__ == "__main__":
    main()
