import os
import secrets
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Union

import requests
from bilibili_api import sync
from bilibili_api.utils.Danmaku import Danmaku
from tqdm import tqdm

from .const import WorkdingDirFolders
from .rewrited_bilibili_api import Video


class DataLoader:
    def __init__(self, working_dir: Path, ffmpeg_exe_path: Path):
        """
        Args:
            working_dir (Path): 工作目录
            ffmpeg_exe_path (Path): ffmpeg.exe路径
        """
        self.working_dir = working_dir
        self.ffmpeg_exe_path = ffmpeg_exe_path

    def bilibili_video(self, bvid: str) -> Path:
        """下载B站视频，并保存到工作目录下 录播 文件夹

        Args:
            bvid (str): BV号
        """
        v = Video(bvid)

        # 配置Session
        session = requests.Session()
        headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36",
            "referer": "https://www.bilibili.com/",
        }
        setattr(session, "headers", headers)  # 防止403

        video_filename = f"{bvid}.mp4"  # 视频文件名
        video_file_path = (
            self.working_dir / WorkdingDirFolders.record.value / video_filename
        )  # 视频文件路径

        if not video_file_path.exists():
            # 获取下载地址json
            下载地址json = sync(v.get_download_url(0))

            # 下载视频
            video_temp_path = (  # 临时视频文件路径
                self.working_dir
                / WorkdingDirFolders.record.value
                / secrets.token_hex(16)
            )
            video_url = 下载地址json["dash"]["video"][0]["base_url"]
            resp = session.get(video_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(video_temp_path, "wb") as file, tqdm(
                desc="下载视频中",
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

            # 下载音频
            audio_temp_path = (  # 临时音频文件路径
                self.working_dir
                / WorkdingDirFolders.record.value
                / secrets.token_hex(16)
            )
            audio_url = 下载地址json["dash"]["audio"][0]["base_url"]
            resp = session.get(audio_url, stream=True)
            total = int(resp.headers.get("content-length", 0))
            with open(audio_temp_path, "wb") as file, tqdm(
                desc="下载音频中",
                total=total,
                unit="iB",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for data in resp.iter_content(chunk_size=1024):
                    size = file.write(data)
                    bar.update(size)

            # 合并视频和音频
            cmd: List[str]
            cmd = [
                str(self.ffmpeg_exe_path),
                "-i",
                str(video_temp_path),
                "-i",
                str(audio_temp_path),
                "-c",
                "copy",
                str(video_file_path),
            ]
            subprocess.run(cmd, capture_output=True)

            # 删除临时文件
            os.remove(video_temp_path)
            os.remove(audio_temp_path)

        return video_file_path

    @staticmethod
    def bilibili_danmaku(bvid: str) -> List[Danmaku]:
        v = Video(bvid)
        danmakus = sync(v.get_danmakus(0))
        return danmakus
