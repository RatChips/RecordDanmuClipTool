import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

import prettytable
from tqdm import tqdm

from .工具 import 把时间转换为秒, 把秒转换为时间
from .常量 import ffmpeg路径, ffprobe路径, 工作目录, 工作目录文件夹


@dataclass
class 切片:
    开始时间: int
    结束时间: int
    标题: str

    def __iter__(self):  # 用于解包
        return iter([self.开始时间, self.结束时间, self.标题])

    def __str__(self):
        return f"【{self.标题}】 {self.开始时间} - {self.结束时间}"


class 切片姬:
    def __init__(self, 视频路径: Path, 切片列表: List[切片]) -> None:
        self.视频路径 = 视频路径
        self.切片列表 = 切片列表
        self.视频长度 = int()

        self._获取视频长度()
        self._校验切片列表()

    def _获取视频长度(self):
        cmd = [ffprobe路径, self.视频路径, "-hide_banner"]
        result = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        alist = [
            x.decode("utf-8").replace("\n", "").strip()
            for x in result.stdout.readlines()
        ]
        duration = re.match(
            r".+?:\s([\d:\.]+),\s?.+", [i for i in alist if "Duration" in i][0]
        ).group(1)
        self.视频长度 = 把时间转换为秒(duration)

    def _校验切片列表(self):
        temp = []
        for 切片 in self.切片列表:
            if 0 <= 切片.开始时间 < 切片.结束时间 <= self.视频长度 and 切片.标题:
                temp.append(切片)
        self.切片列表 = temp

    def 切(self):
        for 开始时间, 结束时间, 标题 in tqdm(self.切片列表, desc="切片中..."):
            文件名 = f"{标题}.mp4"
            cmd = [
                ffmpeg路径,
                "-i",
                self.视频路径,  # 输入视频
                "-vcodec",
                "copy",
                "-acodec",
                "copy",
                "-ss",
                把秒转换为时间(开始时间 + 4),  # 开始时间
                "-to",
                把秒转换为时间(结束时间 + 7),  # 结束时间
                工作目录 / 工作目录文件夹.切片.value / 文件名,  # 输出文件路径
                "-y",
            ]
            # print(" ".join(map(str, cmd)))
            subprocess.run(
                cmd,
                # shell=True,
                stdout=subprocess.PIPE,stderr=subprocess.PIPE
            )

    def 打印所有切片(self):
        table = prettytable.PrettyTable(["标题", "开始时间", "结束时间"])
        table.align = "r"
        for 切片 in self.切片列表:
            table.add_row([切片.标题, 把秒转换为时间(切片.开始时间), 把秒转换为时间(切片.结束时间)])
        print(table)
