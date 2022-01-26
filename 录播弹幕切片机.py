from 工具 import 自动配置, 清屏

自动配置()  # 设置working_dir，设置ffmpeg路径，新建文件夹
清屏()

from 录播数据 import 录播数据加载器,下载B站视频
from 弹幕工厂 import 弹幕工厂
from 切片姬 import 切片姬
from pathlib import Path

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()


def B站():
    bvid = input("请输入录播BV号:")
    # print("请选择视频路径:")

    切片man的uid = input("请输入切片man的uid，用空格分隔:").split(" ")

    视频路径 = 下载B站视频(bvid)
    录播 = 录播数据加载器.从bilibili导入(bvid, 视频路径)
    切片列表 = 弹幕工厂(录播.弹幕路径, 切片man的uid).切片列表
    切片机 = 切片姬(录播.视频路径, 切片列表)

    切片机.打印所有切片()
    切片机.切()


def 录播姬():
    print("请选择视频路径:")
    视频路径 = Path(filedialog.askopenfilename())
    print("请选择弹幕路径:")
    弹幕路径 = Path(filedialog.askopenfilename())

    切片man的uid = input("请输入切片man的uid，用空格分隔:").split(" ")

    录播 = 录播数据加载器.从录播姬导入(视频路径, 弹幕路径)
    弹幕指令 = 弹幕工厂(录播.弹幕路径, 切片man的uid)

    切片列表 = 弹幕指令.切片列表
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


main()
