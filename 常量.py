from enum import Enum
from pathlib import Path


软件名称 = "弹幕切片姬"  # 由RatChips临时起名，并非为最终软件名称


class 工作目录文件夹(Enum):
    录播 = "录播"
    切片 = "切片"
    弹幕 = "弹幕"


class 录播来源(Enum):
    直播回放 = "直播回放"
    录播姬 = "录播姬"
    直播录制 = "直播录制"


ffmpeg路径: Path = Path(Path.home(), "AppData", "Local", 软件名称) / "ffmpeg.exe"
ffprobe路径: Path = Path(Path.home(), "AppData", "Local", 软件名称) / "ffprobe.exe"

工作目录 = Path(Path(Path.home(), "AppData", "Local", 软件名称, "working_folder").read_bytes().decode())

__all__ = ["工作目录", "工作目录文件夹", "录播来源", "ffmpeg路径", "软件名称"]
