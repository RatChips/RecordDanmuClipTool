import os
import re
from typing import List
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
import yaml
from .常量 import 工作目录文件夹, 配置文件路径

root = tk.Tk()
root.withdraw()


config = yaml.load(open(配置文件路径, encoding="utf-8"), Loader=yaml.FullLoader)


def _让用户选择目录() -> Path:
    while not (
        目录 := filedialog.askdirectory(initialdir=Path.cwd(), title="选择工作目录")
    ):  # 防止用户点击取消，返回空目录
        pass
    root.destroy()
    return Path(目录)


def _更新config():
    temp_config = {k: str(v) for k, v in config.items()}
    yaml.dump(temp_config, open(配置文件路径, "w", encoding="utf-8"), allow_unicode=True)


def 自动配置():
    def _更新工作目录():
        print("更新工作目录")
        print("请在弹出的窗口中选择工作目录")
        工作目录 = _让用户选择目录()

        config["工作目录"] = 工作目录

        print(f'新的工作目录为 "{工作目录}"')

    print("开始自动配置")

    print("检测ffmpeg.exe")
    ffmpeg路径 = Path(config["ffmpeg路径"])
    if not ffmpeg路径.exists():
        raise FileNotFoundError(f"ffmpeg.exe不存在，请检查路径 {ffmpeg路径}")

    print("检测ffprobe.exe")
    ffprobe路径 = Path(config["ffprobe路径"])
    if not ffprobe路径.exists():
        raise FileNotFoundError(f"ffprobe.exe不存在，请检查路径 {ffprobe路径}")

    print("检测工作目录")
    工作目录 = Path(config["工作目录"])
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

    工作目录 = Path(config["工作目录"])
    for i in 工作目录文件夹:
        文件夹: Path = 工作目录 / i.value
        if not 文件夹.exists():
            文件夹.mkdir()
    _更新config()


def 把时间转换为秒(time: str) -> int:
    match = re.match(r"^(\d+):(\d+):(\d+).+\d+$", time)
    h, m, s = map(int, match.groups())
    return h * 3600 + m * 60 + s


def 把秒转换为时间(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def 清屏():
    os.system("cls")
