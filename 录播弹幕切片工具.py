from importlib import reload

from 弹幕切片库.工具 import 自动配置

自动配置()  # 设置working_dir，设置ffmpeg路径，新建文件夹

from 弹幕切片库 import 常量

reload(常量)  # 修改工作目录后，需要重新加载常量

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from 弹幕切片库.切片姬 import 切片姬
from 弹幕切片库.弹幕工厂 import 弹幕工厂
from 弹幕切片库.录播数据 import 录播数据加载器

root = tk.Tk()
root.withdraw()


def B站():
    bvid = input("请输入录播BV号:")
    切片man = input("请输入切片man的uid，用空格分隔:").split(" ")

    录播 = 录播数据加载器.从bilibili导入(bvid)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man).导出切片列表()
    切片机 = 切片姬(录播.视频路径, 切片列表)

    切片机.打印所有切片()
    切片机.切()


def 录播姬():
    print("请选择视频路径:")
    视频路径 = Path(filedialog.askopenfilename())
    print("请选择弹幕路径:")
    弹幕路径 = Path(filedialog.askopenfilename())

    切片man = input("请输入切片man的uid，用空格分隔:").split(" ")

    录播 = 录播数据加载器.从录播姬导入(视频路径, 弹幕路径)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man).导出切片列表()
    切片机 = 切片姬(录播.视频路径, 切片列表)

    切片机.打印所有切片()
    切片机.切()


def main():
    功能 = [B站, 录播姬]
    反射列表 = {idx: func for idx, func in enumerate(功能, start=1)}

    for idx in range(1, len(功能) + 1):
        print(f"{idx}. {功能[idx - 1].__name__}")

    while True:
        try:
            选择 = int(input("请输入录播类型:"))
            反射列表[选择]()
            break
        except (KeyError, ValueError):
            print("输入错误，请重新输入")


def debug():
    import os

    if not os.environ.get("DEBUG") == "123456":
        return
    bvid = "BV12b4y1H7ho"
    切片man = "378884133 3723075".split(" ")
    录播 = 录播数据加载器.从bilibili导入(bvid)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man).导出切片列表()
    切片机 = 切片姬(录播.视频路径, 切片列表)

    切片机.打印所有切片()
    切片机.切()
    exit()

if __name__ == "__main__":
    debug()
    main()
