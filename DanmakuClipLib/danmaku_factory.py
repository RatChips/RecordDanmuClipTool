import re
import secrets
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Union, overload

from bilibili_api.utils.Danmaku import Danmaku
from lxml.etree import XML

from .clip_factory import Clip
from .utils import calculate_uid_hash_hex

SEPARATOR = [" ", "，", ","]  # 分隔符
SEPARATOR_REGEX = f'(?:{"|".join(SEPARATOR)})'  # 分隔符正则
DANMAKU_COMMAND_REGEX = (
    rf"@(开切|结束){SEPARATOR_REGEX}(-?\d+)(?:{SEPARATOR_REGEX}(.+))?"  # 弹幕命令正则
)


@dataclass()
class DanmakuCommand:
    """
    弹幕指令
    """

    time: int  # 弹幕在视频中时间
    operation: str  # 操作，[开切/结束]
    offset: int  # 偏移量，单位：秒
    title: Union[str, None] = None  # 切片标题，当“开切”时，title为None


class DanmakuFactory:
    """
    How to use it:
        df = DanmakuFactory(['378884133'])
        1. df.process_danmaku("danmaku.xml") # 录播姬
        2. df.process_damaku(d) #d:Danmaku 直播
        3. df.process_damaku(d) #d:List[Danmaku] 直播回放
    """

    def __init__(self, clipman_uid: Union[List[str], List[int]]):
        self.clipman_uid = clipman_uid
        self.clipman_hash = list(map(calculate_uid_hash_hex, self.clipman_uid))

    def parse_danmaku_command(self, text: str) -> Union[Tuple[str, int, str], None]:
        """
        解析弹幕指令
        """
        match = re.match(DANMAKU_COMMAND_REGEX, text)  # 用正则提取
        if not match:
            return None

        operation, offset, title = match.groups()
        return (operation, int(offset), title)

    def __convert_danmaku_command_to_clips(
        self, danmaku_command: List[DanmakuCommand]
    ) -> List[Clip]:
        clips: List[Clip] = list()
        temp = list()  # 存放开始结束时间
        flag = False
        for dc in danmaku_command:  # 把弹幕指令列表转换为切片列表
            if dc.operation == "开切":
                start_time = dc.time - dc.offset
                if flag is False:
                    flag = not flag
                    temp.append(start_time)
                else:
                    temp.pop()
                    temp.append(start_time)
            elif dc.operation == "结束":
                stop_time = dc.time - dc.offset
                if flag is True:
                    flag = not flag
                    if not dc.title:
                        dc.title = secrets.token_hex(16)
                    clips.append(Clip(temp[0], stop_time, dc.title))
                    temp.clear()
                else:
                    continue
        return clips

    def __bilibili_danmaku(self, danmaku: List[Danmaku]) -> List[Clip]:
        danmaku = list(
            filter(lambda d: d.crc32_id in self.clipman_hash, danmaku)
        )  # 过滤出切片man发的弹幕
        danmaku.sort(key=lambda d: d.dm_time)  # 按弹幕在视频中的时间正序
        danmaku_command: List[DanmakuCommand] = list()
        for d in danmaku:
            if r := self.parse_danmaku_command(d.text):  # 解析弹幕指令
                danmaku_command.append(DanmakuCommand(int(float(d.dm_time)), *r))

        return self.__convert_danmaku_command_to_clips(danmaku_command)

    def __live_danmaku(self, danmaku: Danmaku) -> Union[Tuple[str, int, str], None]:
        if danmaku.crc32_id in self.clipman_hash:
            return self.parse_danmaku_command(danmaku.text)

    def __recorder_danmaku(self, danmaku: Path) -> List[Clip]:
        danmaku_content = danmaku.read_bytes()
        xml = XML(danmaku_content)  # 读取xml，转为etree对象

        data = zip(xml.xpath("//d/@p"), xml.xpath("//d/text()"))  # 提取出p属性和弹幕内容

        # 把xml转为Danmaku列表
        danmakus: List[Danmaku] = list()
        p_attr: str  # p属性
        text: str  # 弹幕内容
        for p_attr, text in data:
            p_attrs = p_attr.split(",")
            dm_time, crc32_id = int(float(p_attrs[0])), calculate_uid_hash_hex(
                p_attrs[-2]
            )
            danmakus.append(Danmaku(dm_time=dm_time, crc32_id=crc32_id, text=text))

        danmakus = list(
            filter(lambda d: d.crc32_id in self.clipman_hash, danmakus)
        )  # 过滤出切片man发的弹幕
        danmakus.sort(key=lambda d: d.dm_time)  # 按弹幕在视频中的时间正序
        danmaku_command: List[DanmakuCommand] = list()
        for d in danmakus:
            if r := self.parse_danmaku_command(d.text):  # 解析弹幕指令
                danmaku_command.append(DanmakuCommand(int(d.dm_time), *r))

        return self.__convert_danmaku_command_to_clips(danmaku_command)

    @overload
    def process_danmaku(self, danmaku: List[Danmaku]) -> List[Clip]:  # B站直播回放
        ...

    @overload
    def process_danmaku(self, danmaku: Danmaku) -> DanmakuCommand:  # live
        ...

    @overload
    def process_danmaku(self, danmaku: Path) -> List[Clip]:  # 录播姬
        ...

    def process_danmaku(
        self, danmaku: Union[List[Danmaku], Danmaku, Path]
    ) -> Union[List[Clip], Tuple[str, int, str], None, DanmakuCommand]:
        """
        处理弹幕
        danmaku: B站直播回放 List[Danmaku]
                 直播弹幕 Danmaku
                 录播姬弹幕 Path

        """
        if isinstance(danmaku, list) and isinstance(danmaku[0], Danmaku):  # B站直播回放
            return self.__bilibili_danmaku(danmaku)

        elif isinstance(danmaku, Danmaku):  # live
            return self.__live_danmaku(danmaku)

        elif isinstance(danmaku, Path):  # 录播姬
            return self.__recorder_danmaku(danmaku)
