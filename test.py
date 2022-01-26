from .工具 import 自动配置, 清屏

自动配置()
清屏()

from .录播数据 import 录播数据加载器
from .弹幕工厂 import 弹幕工厂
from .切片姬 import 切片姬
from pathlib import Path


def B站():
    bvid = "BV12b4y1H7ho"
    视频路径 = Path("D:\DanmuCliper WorkDir\录播\BV12b4y1H7ho.flv")
    切片man的uid = ["378884133"]
    录播 = 录播数据加载器.从bilibili导入(bvid, 视频路径)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man的uid).导出切片列表()
    切片机 = 切片姬(录播.视频路径, 切片列表)

    切片机.打印所有切片()
    切片机.切()


def 录播姬():
    视频路径 = Path(
        "D:\python project\DanmuCliper\录播姬测试数据\录制-23735351-20220119-190827-296-【Genshin】莉莉在原神世界探险.flv"
    )  # 请填入你的视频路径
    弹幕路径 = Path(
        "D:\python project\DanmuCliper\录播姬测试数据\录制-23735351-20220119-190827-296-【Genshin】莉莉在原神世界探险.xml"
    )  # 请填入你的弹幕路径

    切片man的uid = ["378884133"]
    录播 = 录播数据加载器.从录播姬导入(视频路径, 弹幕路径)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man的uid).导出切片列表()

    切片机 = 切片姬(录播.视频路径, 切片列表)
    切片机.打印所有切片()
    切片机.切()


if __name__ == "__main__":
    B站()
    录播姬()
