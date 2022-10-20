# DuLunChe
Python独轮车工具。    
专门为飞天狙直播间开发的独轮车、说书一体化工具。        

## 新功能   
**表情独轮车**：可以发送B站表情包，表情包应该以#开头，后面接表情ID，例如`#room_23197314_16240`，表情ID可以访问`https://api.live.bilibili.com/xlive/web-ucenter/v2/emoticon/GetEmoticons?platform=pc&room_id=<需要查的直播间号>`，返回数据里面会有表情ID的。         
**表情独轮车一些好玩的特性**：
- 发送速度不受限制（它会限制单个表情包的发送速度，但是你几个表情轮流发送就不会有问题）
- 可以在A直播间发送B直播间的表情包，只要你填写了正确的表情ID（但是要保证A直播间是有表情的直播间）    

## 前置    
- Python 3.7+    
- **新版本不用设置cookies，直接运行login.py扫码登录就行**        
- 设置cookies。在目录下新建cookies.txt，把B站的cookies复制粘贴到里面保存。cookies获取方法可以参考：https://github.com/XiaoMiku01/bili-live-heart/blob/master/doc_old/bili.md      

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

