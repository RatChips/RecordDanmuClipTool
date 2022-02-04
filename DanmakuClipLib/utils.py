import platform
import re
import subprocess
import sys
import zlib
from pathlib import Path
from typing import Union

import better_exceptions

from .const import WorkdingDirFolders

better_exceptions.encoding.ENCODING = "utf-8"


def convert_timestr_to_second(timestr: str) -> int:
    """
    00:00:00.00->0
    """
    h, m, s = map(int, map(float, timestr.split(":")))
    return h * 3600 + m * 60 + s


def convert_second_to_timestr(seconds: int) -> str:
    """
    0->00:00:00
    """
    h = seconds // 3600
    m = (seconds - h * 3600) // 60
    s = seconds - h * 3600 - m * 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def get_video_duration(video_file_path: Path, ffprobe_exe_path: Path) -> int:
    """
    获取视频总时长
    """
    cmd = [ffprobe_exe_path, video_file_path, "-hide_banner"]
    result = subprocess.run(cmd, capture_output=True).stderr
    match = re.findall(r"(\d+:\d+:\d+\.\d+)", result.decode())
    assert match

    duration_timestr = match[0]
    duration_sec = convert_timestr_to_second(duration_timestr)
    return duration_sec


def calculate_uid_hash_hex(uid: Union[str, int]) -> str:
    """
    计算用户ID的16进制哈希值
    """
    return hex(zlib.crc32(str(uid).encode()))[2:]


def prepare_working_dir(working_dir: Path):
    for dir in WorkdingDirFolders:
        dir_path: Path = working_dir / dir.value
        dir_path.mkdir(exist_ok=True)


def excepthook(type, value, tb):
    print("".join(better_exceptions.format_exception(type, value, tb)))
    print("PyVersion: ", sys.version)
    print("System: ", platform.system(), platform.architecture()[0])
