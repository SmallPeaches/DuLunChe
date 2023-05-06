import os
try:
    import yaml
    import PIL
    import requests
    import aiohttp
    import qrcode
except ImportError:
    input('Python环境未正确安装，回车自动安装：')
    os.system("python -m pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple")
    print('Python环境安装完成.')