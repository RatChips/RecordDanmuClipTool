from dataclasses import dataclass
from pathlib import Path

import requests
from tqdm import tqdm

from .常量 import 工作目录, 工作目录文件夹, 录播来源


class 录播数据加载器:
    @staticmethod
    def 从bilibili导入(BV号: str):
        视频文件名 = f"{BV号}.flv"
        视频路径 = 工作目录 / 工作目录文件夹.录播.value / 视频文件名
        if not 视频路径.exists():
            api = (
                f"https://tenapi.cn/bilivideo/?url=https://www.bilibili.com/video/{BV号}"
            )
            flv_url = requests.get(api).json()["url"]
            resp = requests.get(flv_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(视频路径, "wb") as file, tqdm(
                desc="下载视频中...",
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

        弹幕路径: Path = 工作目录 / 工作目录文件夹.弹幕.value / (BV号 + ".xml")
        resp = requests.get(f"https://api.bilibili.com/x/player/pagelist?bvid={BV号}")
        cid = resp.json()["data"][0]["cid"]
        resp = requests.get(f"https://comment.bilibili.com/{cid}.xml")
        弹幕路径.write_bytes(resp.content)

        return 录播数据(视频路径, 弹幕路径, 录播来源.直播回放)

    @staticmethod
    def 从录播姬导入(视频路径: Path, 弹幕路径: Path):
        if not 视频路径.exists():
            raise FileNotFoundError(f"{视频路径} not found")
        if not 弹幕路径.exists():
            raise FileNotFoundError(f"{弹幕路径} not found")
        return 录播数据(视频路径, 弹幕路径, 录播来源.录播姬)


@dataclass
class 录播数据:
    视频路径: Path
    弹幕路径: Path
    来源: 录播来源
