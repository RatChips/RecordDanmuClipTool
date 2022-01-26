import re
import secrets
import zlib
from pathlib import Path
from typing import List, Tuple

from lxml.etree import XML

from 切片姬 import 切片


class 弹幕工厂:
    def __init__(self, 弹幕路径: Path, 切片man的uid: List[str]) -> None:
        self.弹幕路径 = 弹幕路径
        self.切片man的uid = 切片man的uid
        self.切片man的hash = list()
        self.弹幕指令列表 = list()  # 秒数,弹幕指令
        self.切片列表 = list()

        self._计算切片man的hash()
        self._从弹幕文件中筛选出切片man发出的弹幕并读取p属性和弹幕指令()
        self._把弹幕指令列表加工成切片列表()

    def _计算切片man的hash(self):
        for uid in self.切片man的uid:
            self.切片man的hash.append(hex(zlib.crc32(uid.encode()))[2:])

    def _从弹幕文件中筛选出切片man发出的弹幕并读取p属性和弹幕指令(self):
        def 是否为切片man发出(属性):
            for i in self.切片man的uid + self.切片man的hash:
                if i in 属性:
                    return True

        xml_data = self.弹幕路径.read_bytes()
        xml = XML(xml_data)
        data = zip(xml.xpath("//d/@p"), xml.xpath("//d/text()"))  # 提取出p属性和弹幕内容
        data = [
            (属性, 弹幕内容) for 属性, 弹幕内容 in data if 弹幕内容[0] == "@"
        ]  # 过滤出弹幕指令(检测弹幕内容是否以@开头切片man可能发非弹幕指令)
        data = [(属性, 弹幕内容) for 属性, 弹幕内容 in data if 是否为切片man发出(属性)]  # 过滤出切片man发出的弹幕

        弹幕发出时间 = [int(float(属性.split(",")[0])) for 属性, _ in data]
        弹幕指令 = list(zip(弹幕发出时间, [x for _, x in data]))
        弹幕指令.sort(key=lambda x: x[0])  # 按照弹幕发出时间排序

        self.弹幕指令列表 = 弹幕指令

    @staticmethod
    def 解析弹幕指令(弹幕指令: str) -> Tuple[str, int, str]:
        分隔符 = [" ", "，", ","]
        分割符正则 = f'(?:{"|".join(分隔符)})'
        弹幕指令正则表达式 = rf"@(开切|结束){分割符正则}(-?\d+)(?:{分割符正则}(.+))?"
        if not (匹配结果 := re.match(弹幕指令正则表达式, 弹幕指令)):
            return None
        操作, 偏移量, 标题 = 匹配结果.groups()
        偏移量 = int(偏移量)
        return (操作, 偏移量, 标题)

    def _把弹幕指令列表加工成切片列表(self):
        temp = list()
        flag = False
        for 时间, 弹幕指令 in self.弹幕指令列表:
            if 匹配结果 := self.解析弹幕指令(弹幕指令):
                操作, 偏移量, 标题 = 匹配结果
                if 操作 == "开切":
                    开始时间 = 时间 - 偏移量
                    if flag is False:
                        flag = not flag
                        temp.append(开始时间)
                    else:
                        temp.pop()
                        temp.append(开始时间)
                elif 操作 == "结束":
                    结束时间 = 时间 - 偏移量
                    if flag is True:
                        flag = not flag
                        if not 标题:
                            标题 = secrets.token_hex(16)
                        self.切片列表.append(切片(temp[0], 结束时间, 标题))
                        temp.clear()
                    else:
                        continue
    def 导出切片列表(self):
        return self.切片列表


if __name__ == "__main__":
    test_bvid = "BV12b4y1H7ho"
    test_cid = "483693069"
    test_url = "https://comment.bilibili.com/483693069.xml"

    xml_path = Path(r"D:\python project\DanmuCliper\483693069.xml")
    d = 弹幕工厂(xml_path, ["378884133"])
    print(d.切片列表)
