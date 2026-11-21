"""文档任务的公共底层：并行策略、选项拆分、路径解析与命令执行。

本模块不注册任何 invoke 任务，只被 ``builder`` / ``make`` 复用，
以保证"任务编排"与"底层能力"各自单一职责。
"""
import os
import shlex
import subprocess
import sys
from multiprocessing import cpu_count

from invoke import Exit

# ---------------------------------------------------------------------------
# 并行构建策略（W-A2 · P1）
#   I-3 根因：串行 Read+Write 阶段总耗时 ~13.4h；-j auto 被 Sphinx fork 语义吞掉
#   分流规则：
#     CI (GITHUB_ACTIONS)          → -j min(cpu_count, 8)   稳定优先，避免 IPC 爆炸
#     本地 POSIX (非 win32)         → -j max(1, cpu_count-1)  留 1 核给桌面响应
#     本地 Windows                  → 空串（不自加 -j）Sphinx 会天然串行，避免告警风暴
# ---------------------------------------------------------------------------


def _parallel_flag() -> str:
    """按运行环境返回 ``-j N`` 字符串；Windows 返回空串（Sphinx 无 fork 只能串行）。"""
    if os.environ.get("GITHUB_ACTIONS"):
        try:
            n = max(1, min(cpu_count() or 1, 8))
        except NotImplementedError:
            n = 4
        return f"-j {n}"
    if sys.platform == "win32":
        return ""
    try:
        n = max(1, (cpu_count() or 2) - 1)
    except NotImplementedError:
        n = 1
    return f"-j {n}"


_PARALLEL_FLAG_DEFAULT = _parallel_flag()


# ---------------------------------------------------------------------------
# 公共底层：env 合并 + shlex 拆分 + 执行
# ---------------------------------------------------------------------------

def _split_cli_args(value: str) -> list[str]:
    """按 shell 风格拆分字符串；Windows 禁用 POSIX 语义。"""
    if not value.strip():
        return []
    return shlex.split(value, posix=os.name != "nt")


def _collect_sphinx_opts(opts: str = "") -> list[str]:
    """合并三层选项优先级：``$SPHINXOPTS`` → ``$O`` → 传入 ``opts``。"""
    args: list[str] = []
    for part in (os.environ.get("SPHINXOPTS", ""), os.environ.get("O", ""), opts):
        args.extend(_split_cli_args(part))
    return args


def _join_shell(tokens: list[str]) -> str:
    """把已拆分的 token 列表重新 shlex.quote 后拼成一条安全 shell 字符串。"""
    return " ".join(shlex.quote(t) for t in tokens if t != "")


def _resolve(c, key: str, override: str | None, default: str | None = None) -> str:
    """解析优先级：显式参数 > 配置字典 > 默认值。"""
    if override is not None:
        return override
    cfg = c.config.get("sphinx", {})
    return cfg.get(key, default)


def _resolve_or(c, key: str, override: str, fallback: str) -> str:
    """当 override 是外部约定默认占位符（``'.'`` / ``'_build'``）时，优先查配置；否则直接用 override。"""
    cfg = c.config.get("sphinx", {})
    if override in (".", "_build"):
        return cfg.get(key) or fallback
    return override


def _run_cmd(c, cmd_tokens: list[str]) -> None:
    """POSIX 默认 pty=True、Windows pty=False；可通过 ``run.pty`` 显式覆盖。"""
    pty = c.config.get("run", {}).get("pty", os.name != "nt")
    c.run(_join_shell(cmd_tokens), pty=pty)


def _run_make_mode(
    target: str,
    sourcedir: str,
    builddir: str,
    opts: str = "",
) -> None:
    """包装 ``sphinx-build -M`` 模式；读取 ``$SPHINXBUILD`` 覆盖可执行路径。"""
    sphinx_build = os.environ.get("SPHINXBUILD", "sphinx-build")
    command = [
        sphinx_build,
        "-M",
        target,
        sourcedir,
        builddir,
        *_collect_sphinx_opts(opts),
    ]
    try:
        completed = subprocess.run(command, check=False)
    except FileNotFoundError as exc:
        raise Exit(
            "The 'sphinx-build' command was not found. Set SPHINXBUILD to the "
            "full path of the executable or add it to PATH."
        ) from exc
    if completed.returncode != 0:
        raise Exit(code=completed.returncode)