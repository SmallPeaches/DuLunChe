# DuLunChe
Python独轮车工具。    
专门为飞天狙直播间开发的独轮车、说书一体化工具。        

## 前置    
- Python 3.7+    
- 设置cookies。在目录下新建cookies.txt，把B站的cookies复制粘贴到里面保存。cookies获取方法：打开B站主页，然后按F12，选择控制台，然后输入`document.cookie`回车得到的就是cookies      

**注意：此cookies包含了B站的登陆信息，不要将它分享给任何人！**

## 使用
独轮车和说书的文本都放在text.txt里面。执行时使用命令行启动（`python main.py`），由于独轮车没啥参数也可以直接双击打开      
- 独轮车模式。文本里面的每一行表示一个独轮车，多个独轮车会循环发送。
- 说书人模式。程序会自动识别分割符然后分句发送。

## 可选参数
- `--cookiespath` 设置cookies的路径，默认./cookies.txt
- `--rid` 设置房间号，默认飞狙直播间(23197314)
- `--interval` 设置独轮车间隔，默认20秒/条
- `--txtpath` 设置文本路径，默认./text.txt
- `--mode` 设置模式，可选auto,shuoshu,dulunche，默认auto（由程序自动判断，如果文本里面有超过40字符的句子就认为是说书，否则开独轮车）

