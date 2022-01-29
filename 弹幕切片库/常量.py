from enum import Enum
from pathlib import Path


class 工作目录文件夹(Enum):
    录播 = "录播"
    切片 = "切片"
    弹幕 = "弹幕"


class 录播来源(Enum):
    直播回放 = "直播回放"
    录播姬 = "录播姬"
    直播录制 = "直播录制"

ffmpeg路径 = Path(__file__).parent.joinpath("ffmpeg.exe")
ffprobe路径 = Path(__file__).parent.joinpath("ffprobe.exe")

工作目录文件路径 = Path(__file__).parent.joinpath("working_dir.dat")
工作目录 = Path(Path(__file__).parent.joinpath("working_dir.dat").read_bytes().decode().strip())

