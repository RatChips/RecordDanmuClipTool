import os
import re
import shutil
import tkinter as tk
from enum import Enum
from pathlib import Path
from tkinter import filedialog

软件名称 = "弹幕切片姬"  # 由RatChips临时起名，并非为最终软件名称


class 工作目录文件夹(Enum):
    录播 = "录播"
    切片 = "切片"
    弹幕 = "弹幕"


root = tk.Tk()
root.withdraw()


def _获取软件数据文件夹() -> Path:
    return Path(Path.home(), "AppData", "Local", 软件名称)


def _让用户选择工作目录() -> Path:
    while not (
        目录 := filedialog.askdirectory(initialdir=Path.cwd(), title="选择工作目录")
    ):  # 防止用户点击取消，返回空目录
        ...
    root.destroy()
    return Path(目录)


def 自动配置():
    def _更新工作目录():
        print("更新工作目录")
        print("请在弹出的窗口中选择工作目录")
        工作目录 = _让用户选择工作目录()
        工作目录文件.write_bytes(str(工作目录).encode())
        print(f'新的工作目录为 "{工作目录}"')

    print("开始自动配置")
    软件数据文件夹 = _获取软件数据文件夹()
    print("检测软件数据文件夹")
    if not 软件数据文件夹.exists():
        软件数据文件夹.mkdir()

    print("检测ffmpeg.exe")
    ffmpeg路径: Path = 软件数据文件夹 / "ffmpeg.exe"
    if not ffmpeg路径.exists():
        shutil.copyfile(Path(__file__).parent / "bak" / "ffmpeg.exe", ffmpeg路径)

    print("检测ffprobe.exe")
    ffprobe路径: Path = 软件数据文件夹 / "ffprobe.exe"
    if not ffprobe路径.exists():
        shutil.copyfile(Path(__file__).parent / "bak" / "ffprobe.exe", ffprobe路径)

    print("检测工作目录文件")
    工作目录文件: Path = 软件数据文件夹 / "working_folder"
    if not 工作目录文件.exists():  # 如果工作目录文件不存在，则创建
        _更新工作目录()
    else:
        工作目录 = 工作目录文件.read_bytes()
        工作目录 = Path(工作目录.decode())
        if not 工作目录.exists():
            _更新工作目录()
        else:
            while not (
                (c := (input(f'是否继续使用工作目录 "{工作目录}" [y/n]?').lower()))
                and len(c) == 1
                and (c in "yn")
            ):  # 只接受y或n
                ...
            if c == "n":
                _更新工作目录()

    工作目录 = Path(
        Path(Path.home(), "AppData", "Local", 软件名称, "working_folder")
        .read_bytes()
        .decode()
    )
    for 文件夹 in 工作目录文件夹:
        文件夹: Path = 工作目录 / 文件夹.value
        if not 文件夹.exists():
            文件夹.mkdir()


def 把时间转换为秒(time: str) -> int:
    match = re.match("^(\d+):(\d+):(\d+).+\d+$", time)
    h, m, s = map(int, match.groups())
    return h * 3600 + m * 60 + s


def 把秒转换为时间(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def 清屏():
    os.system("cls")
