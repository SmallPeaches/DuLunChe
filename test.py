import argparse

from sender.biliapi import BiliLiveAPI

parser = argparse.ArgumentParser()
parser.add_argument('--cookiespath',type=str,default='./cookies.txt')
parser.add_argument('--rid',type=str,default='23197314')
args = parser.parse_args()

with open(args.cookiespath,'r',encoding='utf-8') as f:
    cookies = f.read().strip()
sender = BiliLiveAPI(cookies)

if sender.get_room_info(args.rid)['code'] != 0:
    print('Room error.')

while 1:
    text = input('请输入弹幕文本：')
    rt = sender.send_danmu(args.rid,text)
    if rt['msg'] == '':
        print(f'弹幕 {text} 发送正常.')
    else:
        print(f'弹幕 {text} 被屏蔽, 屏蔽类型{rt["msg"]}.')