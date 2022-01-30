import os
import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path

import requests
from bilibili_api import sync as bilibili_api_sync
from bilibili_api import video
from tqdm import tqdm

from .常量 import ffmpeg路径, 工作目录, 工作目录文件夹, 录播来源


class 录播数据加载器:
    @staticmethod
    def 从bilibili导入(BV号: str):
        session = requests.Session()
        session.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "referer": "https://www.bilibili.com/",
        }

        视频文件名 = f"{BV号}.mp4"
        视频路径 = 工作目录 / 工作目录文件夹.录播.value / 视频文件名

        if not 视频路径.exists():
            # 获取下载地址json
            v = video.Video(BV号)
            下载地址json = bilibili_api_sync(v.get_download_url(0))

            # 下载视频
            video_temp_path = 视频路径.parent.joinpath(secrets.token_hex(16))
            video_url = 下载地址json["dash"]["video"][0]["base_url"]
            resp = session.get(video_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(video_temp_path, "wb") as file, tqdm(
                desc="下载视频中...",
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

            # 下载音频
            audio_temp_path = 视频路径.parent.joinpath(secrets.token_hex(16))
            audio_url = 下载地址json["dash"]["audio"][0]["base_url"]
            resp = session.get(audio_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(audio_temp_path, "wb") as file, tqdm(
                desc="下载音频中...",
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

            # 合并视频和音频
            cmd = [
                ffmpeg路径,
                "-i",
                video_temp_path,
                "-i",
                audio_temp_path,
                "-c",
                "copy",
                视频路径,
            ]
            subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # 删除临时文件
            os.remove(video_temp_path)
            os.remove(audio_temp_path)

        # 下载弹幕
        弹幕路径: Path = 工作目录 / 工作目录文件夹.弹幕.value / (BV号 + ".xml")
        resp = session.get(f"https://api.bilibili.com/x/player/pagelist?bvid={BV号}")
        cid = resp.json()["data"][0]["cid"]
        resp = session.get(f"https://comment.bilibili.com/{cid}.xml")
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
