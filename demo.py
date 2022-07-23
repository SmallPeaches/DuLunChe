import argparse
import time

from sender.biliapi import BiliLiveAPI

parser = argparse.ArgumentParser()
parser.add_argument('--cookiespath',type=str,default='./cookies.txt')
parser.add_argument('--rid',type=str,default='23197314')
parser.add_argument('--timesplit',type=float,default=20)
args = parser.parse_args()

with open(args.cookiespath,'r',encoding='utf-8') as f:
    cookies = f.read().strip()
sender = BiliLiveAPI(cookies)

if sender.get_room_info(args.rid)['code'] != 0:
    print('Room error.')

while 1:
    text = input('请输入弹幕文本和次数：')
    try:
        if len(text.split(' ')) > 1:
            num = int(text.split(' ')[-1])
            text = ' '.join(text.split(' ')[:-1])
    except:
        num = 1
    
    for i in range(num):
        rt = sender.send_danmu(args.rid,text)
        if rt.get('msg','') == '':
            print(f'独轮车 {i+1}/{num}: {text}.')
            time.sleep(args.timesplit)
        else:
            print(f'独轮车 {i+1}/{num} was killed ({rt["msg"]}): {text}.')
            time.sleep(1.0)
    print('独轮车结束.')