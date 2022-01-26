from enum import Enum
from pathlib import Path
import yaml


class 工作目录文件夹(Enum):
    录播 = "录播"
    切片 = "切片"
    弹幕 = "弹幕"


class 录播来源(Enum):
    直播回放 = "直播回放"
    录播姬 = "录播姬"
    直播录制 = "直播录制"


配置文件路径 = Path(__file__).parent.parent / "config.yaml"
config = yaml.load(open(配置文件路径, encoding="utf-8"), Loader=yaml.FullLoader)

ffmpeg路径 = Path(config["ffmpeg路径"])
ffprobe路径 = Path(config["ffprobe路径"])

工作目录 = Path(config["工作目录"])
