import sys
from pathlib import Path

import easygui

from DanmakuClipLib import ClipFactory, DanmakuFactory, DataLoader
from DanmakuClipLib.utils import excepthook, prepare_working_dir

sys.excepthook = excepthook

try:
    import msvcrt  # windows平台独有的console I/O库
except ModuleNotFoundError:
    raise RuntimeError("目前只支持Windows系统")

print("请选择工作目录：")
assert (temp := easygui.diropenbox(msg="请选择工作目录", title="选择工作目录")), "请选择工作目录"
working_dir = Path(temp)

ffmepg_exe_path = Path(__file__).parent / "bin" / "ffmpeg.exe"
ffprobe_exe_path = Path(__file__).parent / "bin" / "ffprobe.exe"

prepare_working_dir(working_dir)  # 创建工作目录下文件夹


def main():
    print("录播来源：\n\t1. bilibili\n\t2. 录播姬", flush=True)
    print("请输入数字：", end="", flush=True)
    choice = msvcrt.getwche()  # 获取一位unicode字符
    print(flush=True)
    assert choice in "12", "输入错误"

    if choice == "1":
        bvid = input("请输入BV号：")
        dl = DataLoader(working_dir, ffmepg_exe_path)
        video_path = dl.bilibili_video(bvid)
        danmaku = dl.bilibili_danmaku(bvid)
    elif choice == "2":
        print("请选择视频")
        temp = easygui.fileopenbox(msg="请选择视频")
        assert temp, "请选择视频"
        video_path = Path(temp)

        print("请选择弹幕")
        temp = easygui.fileopenbox(msg="请选择弹幕", default="*.xml")
        assert temp, "请选择弹幕"
        danmaku = Path(temp)

    clipman_uid = input("请输入切片man的uid（用空格分隔）：").split(" ")
    assert all(x.isdigit() for x in clipman_uid), "请输入正确的uid"

    df = DanmakuFactory(clipman_uid)
    clips = df.process_danmaku(danmaku)

    cf = ClipFactory(video_path, clips, working_dir, ffmepg_exe_path, ffprobe_exe_path)
    cf.print_clips()
    cf.make_clips()


if __name__ == "__main__":
    main()
