import os
from pathlib import Path

source = [
    "https://pypi.tuna.tsinghua.edu.cn/simple",
    "https://pypi.mirrors.ustc.edu.cn/simple/",
    "https://pypi.douban.com/simple/",
]

requirements_path = Path(__file__).parent.joinpath("requirements.txt")

for src in source:
    if os.system(f"pip install -r {requirements_path} -i {src} --no-cache-dir") == 0:
        break
