import os

source = [
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://pypi.mirrors.ustc.edu.cn/simple/",
    "https://pypi.douban.com/simple/",
]

for src in source:
    if os.system(f"pip install -r requirements.txt -i {src} --no-cache-dir") == 0:
        break