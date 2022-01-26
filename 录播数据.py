from bilibili_api import video, sync,Credential
import aiohttp,os,asyncio
from dataclasses import dataclass
from pathlib import Path

import requests

from 常量 import 工作目录, 工作目录文件夹, 录播来源, ffmpeg路径


class YouGetError(Exception):
    ...


class 录播数据加载器:
    @staticmethod
    def 从bilibili导入(BV号: str, 视频路径: Path):
        if not 视频路径.exists():
            raise FileNotFoundError(f"{视频路径} not found")

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


async def 下载b站视频_(bvid_,video_title):
    SESSDATA = ""
    BILI_JCT = ""
    BUVID3 = ""
    # 实例化 Credential 类
    credential = Credential(sessdata=SESSDATA, bili_jct=BILI_JCT, buvid3=BUVID3)
    # 实例化 Video 类
    v = video.Video(bvid=bvid_, credential=credential)
    # 获取视频下载链接
    url = await v.get_download_url(0)
    # 视频轨链接
    video_url = url["dash"]["video"][0]['baseUrl']
    # 音频轨链接
    audio_url = url["dash"]["audio"][0]['baseUrl']
    # 视频标题
    # video_title=str(v.get_info()['title']).replace(' ','')
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Referer": "https://www.bilibili.com/"
    }
    async with aiohttp.ClientSession() as sess:
        # 下载视频流
        async with sess.get(video_url, headers=HEADERS,timeout=0) as resp:
            length = resp.headers.get('content-length')
            print(工作目录 / 工作目录文件夹.录播.value / Path("video_temp.m4s"))
            with open(工作目录 / 工作目录文件夹.录播.value / Path("video_temp.m4s"), 'wb') as f:
                process = 0
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break

                    process += len(chunk)
                    print(f'下载视频流 {process} / {length}')
                    f.write(chunk)

        # 下载音频流
        async with sess.get(audio_url, headers=HEADERS) as resp:
            length = resp.headers.get('content-length')
            with open(工作目录 / 工作目录文件夹.录播.value / Path("audio_temp.m4s"), 'wb') as f:
                process = 0
                while True:
                    chunk = await resp.content.read(1024)
                    if not chunk:
                        break

                    process += len(chunk)
                    print(f'下载音频流 {process} / {length}')
                    f.write(chunk)

        # 混流
        print('混流中')
        
        # print(path+'/录播/video_temp.m4s '+'-i '+path+'/录播/audio_temp.m4s -vcodec copy -acodec copy '+path+'/录播/'+video_title+'.mp4')
        
        
        video_temp = 工作目录 / 工作目录文件夹.录播.value / Path("video_temp.m4s")
        audio_temp = 工作目录 / 工作目录文件夹.录播.value / Path("audio_temp.m4s")
        file_name = 工作目录 / 工作目录文件夹.录播.value / Path(video_title)
        print(f'{ffmpeg路径} -i {video_temp} -i {audio_temp} -vcodec copy -acodec copy "{file_name}.mp4"')
        os.system(f'{ffmpeg路径} -i {video_temp} -i {audio_temp} -vcodec copy -acodec copy "{file_name}.mp4"')

        # 删除临时文件
        os.remove(工作目录 / 工作目录文件夹.录播.value / Path("video_temp.m4s"))
        os.remove(工作目录 / 工作目录文件夹.录播.value / Path("audio_temp.m4s"))
    return 工作目录 / 工作目录文件夹.录播.value / Path(video_title+'.mp4')

def 下载B站视频(bvid):
    v = video.Video(bvid=bvid)
    video_title=str(sync(v.get_info())['title']).replace('|','-').replace(' ','-')
    return asyncio.get_event_loop().run_until_complete(下载b站视频_(bvid,video_title))






@dataclass
class 录播数据:
    视频路径: Path
    弹幕路径: Path
    来源: str


__all__ = ["录播数据加载器", "录播数据"]
