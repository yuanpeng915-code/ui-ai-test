"""
description: 从 step_impl/ 下清洗步骤说明。支持传入目录或文件名，按 all/file/fun 三种模式查看。
usage:
    python step_doc_extractor.py [目录|文件名] [all|file|fun]
    - 目录: 如 asset / profile/om -> 递归该目录下所有 step 文件
    - 文件: 如 search_asset.py / search_asset / asset/management/search_asset.py
    不传参则交互式输入。
"""
import argparse
import ast
import sys
from pathlib import Path
from typing import Literal

def _find_project_root() -> Path:
    """从当前脚本向上查找包含 step_impl/ 的目录作为项目根。"""
    for parent in Path(__file__).resolve().parents:
        if (parent / "step_impl").is_dir():
            return parent
    raise RuntimeError("未找到包含 step_impl/ 的项目根目录")


ROOT = _find_project_root()
STEP_IMPL_DIR = ROOT / "step_impl"

ViewMode = Literal["all", "file", "fun"]

SEP_MAIN = "=" * 60
SEP_SUB = "-" * 40


def resolve_step_files(name: str) -> list[Path]:
    """在 step_impl/ 下解析目录或文件名，返回匹配的 .py 文件列表（排除 __init__.py）。

    支持两种输入:
    - 目录: 如 'asset' / 'profile/om' -> 递归返回该目录下所有 step .py 文件
    - 文件: 精确或模糊匹配，返回命中的 .py 文件
      精确: 'search_asset.py' / 'asset/management/search_asset.py'
      模糊: 'search_asset' -> '*search_asset*.py'
    """
    name = name.replace("\\", "/").strip().strip("/")

    # 1) 目录: 拼接 step_impl/ 直接判断，递归返回所有 step 文件
    direct_dir = STEP_IMPL_DIR / name
    if direct_dir.is_dir():
        return sorted(
            p for p in direct_dir.rglob("*.py")
            if p.name != "__init__.py"
        )

    # 2) 文件: 按文件名递归匹配
    patterns: list[str] = []
    patterns.append(name)                              # 精确: search_asset.py 或 asset/management/search_asset.py
    if not name.endswith(".py"):
        patterns.append(f"*{name}*.py")                # 模糊: search_asset -> *search_asset*.py
    patterns.append(f"*{name}*")                       # 更宽模糊

    seen: set[Path] = set()
    candidates: list[Path] = []
    for pat in patterns:
        for p in STEP_IMPL_DIR.rglob(pat):
            if p.suffix != ".py" or p.name == "__init__.py":
                continue
            if p not in seen:
                seen.add(p)
                candidates.append(p)
        if candidates:
            break
    return candidates


def _is_step_decorator(deco: ast.expr) -> bool:
    """判断装饰器是否为 @step(...) 或 @step。"""
    target = deco.func if isinstance(deco, ast.Call) else deco
    if isinstance(target, ast.Name) and target.id == "step":
        return True
    if isinstance(target, ast.Attribute) and target.attr == "step":
        return True
    return False


def _is_docstring(stmt: ast.stmt) -> bool:
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Constant)
        and isinstance(stmt.value.value, str)
    )


def extract_file_docstring(source: str) -> str:
    """提取文件头部 module docstring 的原始文本块。"""
    tree = ast.parse(source)
    if not tree.body or not _is_docstring(tree.body[0]):
        return "(该文件无头部 docstring)"
    node = tree.body[0]
    lines = source.splitlines()
    return "\n".join(lines[node.lineno - 1: node.end_lineno])


def extract_step_functions(source: str) -> list[str]:
    """提取所有 @step 函数的描述块（装饰器 + def + docstring），保持源码原样。"""
    tree = ast.parse(source)
    lines = source.splitlines()
    blocks: list[str] = []

    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        if not any(_is_step_decorator(d) for d in node.decorator_list):
            continue

        # 起始行：第一个装饰器（无装饰器则 def 行）
        start = min((d.lineno for d in node.decorator_list), default=node.lineno)
        # 结束行：docstring 结束行（无 docstring 则只取 def 行）
        if node.body and _is_docstring(node.body[0]):
            end = node.body[0].end_lineno
        else:
            end = node.lineno

        blocks.append("\n".join(lines[start - 1: end]))
    return blocks


def render(file_path: Path, mode: ViewMode) -> str:
    """按模式渲染输出。"""
    source = file_path.read_text(encoding="utf-8")
    rel = file_path.relative_to(ROOT).as_posix()
    parts: list[str] = [f"文件: {rel}", SEP_MAIN]

    if mode in ("file", "all"):
        parts.append(extract_file_docstring(source))

    if mode in ("fun", "all"):
        fun_blocks = extract_step_functions(source)
        if mode == "all":
            parts.append(SEP_SUB)
        if not fun_blocks:
            parts.append("(该文件无 @step 函数)")
        else:
            for i, block in enumerate(fun_blocks):
                if i > 0:
                    parts.append(SEP_SUB)
                parts.append(block)

    return "\n".join(parts)


def list_available_files() -> list[str]:
    """列出 step_impl/ 下所有可用 step 文件（路径相对 step_impl/，排除 __init__.py）。"""
    files = [
        p.relative_to(STEP_IMPL_DIR).as_posix()
        for p in STEP_IMPL_DIR.rglob("*.py")
        if p.name != "__init__.py"
    ]
    return sorted(files)


def list_available_dirs() -> list[str]:
    """列出 step_impl/ 下含 step 文件的子目录（路径相对 step_impl/）。"""
    dirs: set[str] = set()
    for p in STEP_IMPL_DIR.rglob("*.py"):
        if p.name == "__init__.py" or p.parent == STEP_IMPL_DIR:
            continue
        dirs.add(p.parent.relative_to(STEP_IMPL_DIR).as_posix())
    return sorted(dirs)


def print_available() -> None:
    """向 stderr 打印 step_impl/ 下可用的目录与文件。"""
    print("可用目录:", file=sys.stderr)
    for d in list_available_dirs():
        print(f"  {d}", file=sys.stderr)
    print("可用文件:", file=sys.stderr)
    for f in list_available_files():
        print(f"  {f}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="从 step_impl/ 下清洗步骤说明，支持目录或文件名",
        usage="python .claude/scripts/step_doc_extractor.py [目录|文件名] [all|file|fun]",
    )
    parser.add_argument("target", nargs="?", help="step 目录或文件名（如 asset / profile/om / search_asset.py）")
    parser.add_argument("mode", nargs="?", choices=["all", "file", "fun"],
                        help="查看模式: all(默认) / file(文件头部描述) / fun(所有函数步骤描述)")
    args = parser.parse_args()

    target: str = args.target or input("请输入步骤目录或文件名: ").strip()
    mode: ViewMode = args.mode or "all"

    if not target:
        print("未输入目标，可用目录/文件如下:", file=sys.stderr)
        print_available()
        return 1

    file_paths = resolve_step_files(target)
    if not file_paths:
        print(f"未找到匹配目标: {target}", file=sys.stderr)
        print("可用目录/文件如下:", file=sys.stderr)
        print_available()
        return 1

    outputs = [render(p, mode) for p in file_paths]
    print("\n\n".join(outputs))
    return 0


if __name__ == "__main__":
    sys.exit(main())
