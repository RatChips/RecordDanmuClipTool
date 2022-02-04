import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List

import prettytable
from tqdm import tqdm

from .const import WorkdingDirFolders
from .utils import convert_second_to_timestr, get_video_duration


@dataclass
class Clip:
    start_sec: int
    stop_sec: int
    title: str


class ClipFactory:
    def __init__(
        self,
        video_file_path: Path,
        clips_list: List[Clip],
        working_dir: Path,
        ffmpeg_exe_path: Path,
        ffprobe_exe_path: Path,
    ):
        self.working_dir = working_dir
        self.video_file_path = video_file_path
        self.clips_list = clips_list
        self.ffmpeg_exe_path = ffmpeg_exe_path
        self.ffprobe_exe_path = ffprobe_exe_path

        self.video_duration = get_video_duration(
            self.video_file_path, self.ffprobe_exe_path
        )

        self.__校验切片列表()

    def __校验切片列表(self):
        def __check(clip: Clip):
            rules = [
                # 切片开始时间必须大于等于0
                0 <= clip.start_sec,
                # 切片开始时间必须小于切片结束时间
                clip.start_sec < clip.stop_sec,
                # 切片结束时间必须小于视频总时长
                clip.stop_sec <= self.video_duration,
                # 切片标题不能为空
                clip.title,
            ]
            return all(rules)

        self.clips_list = list(filter(__check, self.clips_list))

    def make_clips(self):
        with tqdm(total=len(self.clips_list)) as pbar:
            for clip in self.clips_list:
                pbar.set_description(f"切片中 【{clip.title}】")
                clip_filename = f"{clip.title}.mp4"
                clip_filepath = (
                    self.working_dir / WorkdingDirFolders.clip.value / clip_filename
                )
                cmd = [
                    self.ffmpeg_exe_path,
                    "-i",
                    self.video_file_path,  # 输入视频
                    "-vcodec",
                    "copy",
                    "-acodec",
                    "copy",
                    "-ss",
                    convert_second_to_timestr(clip.start_sec + 4),  # 开始时间
                    "-to",
                    convert_second_to_timestr(clip.stop_sec + 7),  # 结束时间
                    clip_filepath,
                    "-y",
                ]
                subprocess.run(cmd, capture_output=True)
                pbar.update(1)

    def print_clips(self):
        if not self.clips_list:
            return
        table = prettytable.PrettyTable(["标题", "开始时间", "结束时间"])
        table.align = "r"
        for c in self.clips_list:
            table.add_row(
                [
                    c.title,
                    convert_second_to_timestr(c.start_sec),
                    convert_second_to_timestr(c.stop_sec),
                ]
            )
        print(table)
