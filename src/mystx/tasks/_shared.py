"""跨任务域共享的 invoke 执行原语。

本模块只放与具体领域无关的能力：选项拆分、安全拼接、命令执行。
任何任务域（``doc`` 及未来的其他域）都应从这里复用，域之间不得互相 import。
"""
import os
import shlex


def split_cli_args(value: str) -> list[str]:
    """按 shell 风格拆分字符串；Windows 禁用 POSIX 语义。"""
    if not value.strip():
        return []
    return shlex.split(value, posix=os.name != "nt")


def join_shell(tokens: list[str]) -> str:
    """把已拆分的 token 列表重新 shlex.quote 后拼成一条安全 shell 字符串。"""
    return " ".join(shlex.quote(t) for t in tokens if t != "")


def run_cmd(c, cmd_tokens: list[str]) -> None:
    """POSIX 默认 pty=True、Windows pty=False；可通过 ``run.pty`` 显式覆盖。"""
    pty = c.config.get("run", {}).get("pty", os.name != "nt")
    c.run(join_shell(cmd_tokens), pty=pty)
