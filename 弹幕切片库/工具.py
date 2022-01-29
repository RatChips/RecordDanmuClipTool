import re
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from .常量 import ffmpeg路径, ffprobe路径, 工作目录文件夹, 工作目录文件路径

root = tk.Tk()
root.withdraw()


def _让用户选择目录() -> Path:
    while not (
        目录 := filedialog.askdirectory(initialdir=Path.cwd(), title="选择工作目录")
    ):  # 防止用户点击取消，返回空目录
        pass
    root.destroy()
    return Path(目录)


def 自动配置():
    def _更新工作目录():
        print("更新工作目录")
        print("请在弹出的窗口中选择工作目录")
        工作目录 = _让用户选择目录()

        工作目录文件路径.write_bytes(str(工作目录).encode())

        print(f'新的工作目录为 "{工作目录}"')

    print("开始自动配置")

    print("检测ffmpeg.exe")
    if not ffmpeg路径.exists():
        raise FileNotFoundError(f"ffmpeg.exe不存在，请检查路径 {ffmpeg路径}")

    print("检测ffprobe.exe")
    if not ffprobe路径.exists():
        raise FileNotFoundError(f"ffprobe.exe不存在，请检查路径 {ffprobe路径}")

    工作目录 = Path(工作目录文件路径.read_bytes().decode().strip())
    print("检测工作目录")
    if not 工作目录.exists():
        _更新工作目录()
    else:
        while not (
            (c := (input(f'是否继续使用工作目录 "{工作目录}" [y/n]?').lower()))
            and len(c) == 1
            and (c in "yn")
        ):  # 只接受y或n
            pass
        if c == "n":
            _更新工作目录()

    工作目录 = Path(工作目录文件路径.read_bytes().decode().strip())
    for i in 工作目录文件夹:
        文件夹: Path = 工作目录 / i.value
        if not 文件夹.exists():
            文件夹.mkdir()


def 把时间转换为秒(time: str) -> int:
    match = re.match(r"^(\d+):(\d+):(\d+).+\d+$", time)
    h, m, s = map(int, match.groups())
    return h * 3600 + m * 60 + s


def 把秒转换为时间(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:02d}"
