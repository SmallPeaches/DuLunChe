import argparse
import time

from sender.sender import Sender

parser = argparse.ArgumentParser()
parser.add_argument('--cookiespath',type=str,default='./cookies.txt')
parser.add_argument('--rid',type=str,default='23197314')
parser.add_argument('--timesplit',type=float,default=20)
args = parser.parse_args()

with open(args.cookiespath,'r',encoding='utf-8') as f:
    cookies = f.read().strip()
sender = Sender(cookies,rid=args.rid)

while 1:
    text = input('请输入弹幕文本、次数和间隔：')
    num = 1
    interval = args.timesplit
    try:
        if len(text.split(' ')) > 2:
            interval = float(text.split(' ')[-1])
            num = int(text.split(' ')[-2])
            text = ' '.join(text.split(' ')[:-2])
        elif len(text.split(' ')) > 1:
            num = int(text.split(' ')[-1])
            text = ' '.join(text.split(' ')[:-1])
    except:
        pass
    
    i = 0
    while i < num:
        for t in text.split(','):
            if not t:
                continue
            status,msg = sender.sendx(t)
            if status:
                print(f'独轮车 {i+1}/{num}: {t}.')
                time.sleep(interval)
            else:
                print(f'独轮车 {i+1}/{num} was killed ({msg}): {t}.')
                time.sleep(1.0)
            i += 1
    print('独轮车结束.')