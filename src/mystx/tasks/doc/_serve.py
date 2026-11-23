"""本地 HTTP 预览服务：端口探测、子进程托管与浏览器唤起。

由 ``builder.browse`` 调用；把服务器生命周期与 invoke 任务编排分离，
便于单独测试端口选择与进程回收。
"""
import socket
import subprocess
import sys
import webbrowser
from pathlib import Path


def _free_port(host: str, port: int) -> int:
    """从 ``port`` 起返回第一个可连接失败的端口（即当前无人监听）。"""
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex((host, port)) != 0:
                return port
        port += 1


def serve(directory: Path, port: int = 8000, host: str = "127.0.0.1") -> None:
    """在 ``directory`` 启动 ``python -m http.server`` 并打开浏览器，直至进程退出。"""
    port = _free_port(host, port)
    url = f"http://{host}:{port}/"
    print(f"[browse] 启动 HTTP 服务器：{url}  (目录={directory})；Ctrl+C 退出")
    server = subprocess.Popen(
        [sys.executable, "-m", "http.server", str(port), "--bind", host],
        cwd=str(directory),
    )
    webbrowser.open(url)
    try:
        server.wait()
    except KeyboardInterrupt:
        server.terminate()
