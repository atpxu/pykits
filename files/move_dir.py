#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import os
import shutil
import sys

IMG_SUFFIXES = {
    "jpg", "jpeg", "png", "bmp", "gif", "webp", "tif", "tiff", "svg", "heic", "heif"
}
TXT_SUFFIXES = {
    "txt", "md", "csv", "tsv", "json", "yaml", "yml", "xml", "ini", "log", "toml"
}


def parse_args():
    parser = argparse.ArgumentParser(
        prog="move_dir.py",
        description=(
            "按条件匹配并移动文件（默认仅打印 mv 命令；加 -a/--action 才执行）。\n"
            "匹配类型：\n"
            "  len    —— 按文件名长度（不含路径与后缀）等于指定值\n"
            "  str    —— 文件名包含指定字符串（不含路径与后缀，不区分大小写）\n"
            "  subfix —— 按后缀匹配（不区分大小写；可带/不带点）\n"
            "  type   —— 文件类型，目前支持 img/txt（按常见后缀识别）\n"
            "递归模式（-r）下，会在目标目录下镜像创建源目录的子目录结构。"
        ),
        formatter_class=argparse.RawTextHelpFormatter,
        add_help=True,
    )
    parser.add_argument("-s", "--source", required=True, help="源目录 SRC_DIR")
    parser.add_argument("-t", "--target", required=True, help="目标目录 TRG_DIR")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归遍历源目录")
    parser.add_argument(
        "-m", "--match", required=True,
        choices=["len", "str", "type", "subfix"],
        help="匹配类型：len/str/type/subfix")
    parser.add_argument(
        "-v", "--value", required=True,
        help="匹配值：len=整数；str=子串；subfix=后缀；type=img|txt")
    parser.add_argument(
        "-a", "--action", action="store_true",
        help="执行移动（默认仅打印命令）")
    parser.add_argument(
        "-p", "--on-exist-policy", choices=["skip", "rename", "overwrite"],
        default="skip",
        help="目标已存在时的处理策略：skip(跳过, 默认)/rename(自动重命名)/overwrite(覆盖)")

    return parser.parse_args()


def norm_suffix(s: str) -> str:
    return s.lower().lstrip(".")


def get_suffix(fname: str) -> str:
    return norm_suffix(os.path.splitext(fname)[1])


def base_name_no_ext(fname: str) -> str:
    """返回不含扩展名的文件名"""
    return os.path.splitext(fname)[0]


def match_len(fname: str, val: str) -> bool:
    try:
        target = int(val)
    except ValueError:
        return False
    name = base_name_no_ext(fname)
    return len(name) == target


def match_str(fname: str, val: str) -> bool:
    name = base_name_no_ext(fname)
    return val.lower() in name.lower()


def match_subfix(fname: str, val: str) -> bool:
    return get_suffix(fname) == norm_suffix(val)


def match_type(fname: str, val: str) -> bool:
    suf = get_suffix(fname)
    if val.lower() == "img":
        return suf in IMG_SUFFIXES
    if val.lower() == "txt":
        return suf in TXT_SUFFIXES
    return False


def should_select(fname: str, mtype: str, mval: str) -> bool:
    if mtype == "len":
        return match_len(fname, mval)
    elif mtype == "str":
        return match_str(fname, mval)
    elif mtype == "subfix":
        return match_subfix(fname, mval)
    elif mtype == "type":
        return match_type(fname, mval)
    else:
        return False


def iter_files(src: str, recursive: bool):
    if recursive:
        for root, dirs, files in os.walk(src):
            for f in files:
                yield root, f
    else:
        for f in os.listdir(src):
            p = os.path.join(src, f)
            if os.path.isfile(p):
                yield src, f


def resolve_conflict(tgt_dir: str, fname: str, policy: str) -> str | None:
    """根据 on-exist 策略生成目标路径。若跳过则返回 None。"""
    dst_path = os.path.join(tgt_dir, fname)

    if not os.path.exists(dst_path):
        return dst_path

    if policy == "skip":
        print(f"[SKIP] 已存在: {dst_path}")
        return None
    elif policy == "rename":
        stem, ext = os.path.splitext(fname)
        i = 1
        while True:
            new_name = f"{stem}_{i}{ext}"
            dst_path = os.path.join(tgt_dir, new_name)
            if not os.path.exists(dst_path):
                return dst_path
            i += 1
    elif policy == "overwrite":
        return dst_path
    return None


def main():
    args = parse_args()
    src = os.path.abspath(args.source)
    dst = os.path.abspath(args.target)

    if not os.path.isdir(src):
        print(f"[ERROR] 源目录不存在或不是目录: {src}", file=sys.stderr)
        sys.exit(2)

    total = 0
    selected = 0
    moved = 0

    os.makedirs(dst, exist_ok=True)

    for root, fname in iter_files(src, args.recursive):
        src_path = os.path.join(root, fname)
        if not os.path.isfile(src_path):
            continue
        total += 1

        if not should_select(fname, args.match, args.value):
            continue

        selected += 1
        rel_dir = os.path.relpath(root, src) if args.recursive else "."
        tgt_dir = dst if rel_dir == "." else os.path.join(dst, rel_dir)
        os.makedirs(tgt_dir, exist_ok=True)

        dst_path = resolve_conflict(tgt_dir, fname, args.on_exist)
        if dst_path is None:
            continue

        print(f"mv '{src_path}' '{dst_path}'")
        if args.action:
            try:
                shutil.move(src_path, dst_path)
                moved += 1
            except Exception as e:
                print(f"[ERROR] 移动失败: {src_path} -> {dst_path} | {e}", file=sys.stderr)

    print(f"\n[SUMMARY] 总文件: {total}, 命中: {selected}, 实际移动: {moved if args.action else 0}")
    if not args.action:
        print("[INFO] 当前为 Dry-Run（仅打印命令）。加 -a/--action 才执行移动。")


if __name__ == "__main__":
    main()
