import argparse
import os
import re
import time
from sender.biliapi import BiliLiveAPI

def readtxt(fpath,mode='book'):
    text = []
    if mode == 'dulunche':
        with open(fpath,'r',encoding='utf-8') as f:
            txt = f.readlines()
            for t in txt:
                t = t.strip()
                if len(t) > 0:
                    text.append(t[:30])
    else:
        with open(fpath,'r',encoding='utf-8') as f:
            txt = f.read()
            str_list = re.split(r"[\n,，.。～！、;；]|(\s)",txt)
            str_list = [s for s in str_list if s and len(s.strip())>0]
            p = 0
            while p < len(str_list):
                t = str_list[p]
                if len(t) < 10:
                    while p < len(str_list)-1 and len(t+' '+str_list[p+1]) < 30:
                        t += ' '+str_list[p+1]
                        p += 1
                    text.append(t)
                    p += 1
                elif len(t) > 30:
                    if len(t) < 60:
                        t0 = t[:len(t)//2]
                        t1 = t[len(t)//2:]
                    else:
                        t0 = t[0:30]
                        t1 = t[30:60]
                    text.append(t0)
                    text.append(t1)
                    p += 1
                else:
                    text.append(t)
                    p += 1

    return text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookiespath',type=str,default='./cookies.txt')
    parser.add_argument('--rid',type=str,default='23197314')
    parser.add_argument('--txtpath',type=str,default='./text.txt')
    parser.add_argument('--timesplit',type=float,default=20)
    parser.add_argument('--mode',choices=['book','dulunche'],default='book')
    args = parser.parse_args()

    text = readtxt(args.txtpath,mode=args.mode)
    print(f'独轮车总数{len(text)}, 间隔{args.timesplit}sec.')
    with open(args.cookiespath,'r',encoding='utf-8') as f:
        cookies = f.read().strip()
    sender = BiliLiveAPI(cookies)

    if sender.get_room_info(args.rid)['code'] != 0:
        print('Room error.')
    
    dm_cnt = 0
    kill_cnt = 0
    
    while 1:
        if len(text) < 1:
            print('No text, waiting...')
            time.sleep(1)

            new_text = readtxt(args.txtpath,mode=args.mode)
            if new_text != text:
                text = new_text
                print('refresh text.')
                break

            continue

        for word_cnt,txt in enumerate(text):
            rt = sender.send_danmu(args.rid,txt)
            dm_cnt += 1
            if rt['msg'] != '':
                kill_cnt += 1
                print(f'独轮车 {word_cnt+1}/{len(text)} was killed ({rt["msg"]}): {txt}.'+' '*30)
                time.sleep(1)
            else:
                print(f'独轮车 {word_cnt+1}/{len(text)}, total {dm_cnt:04d}: {txt}.'+' '*30)
                time.sleep(args.timesplit)

            new_text = readtxt(args.txtpath,mode=args.mode)
            if new_text != text:
                text = new_text
                print('\nrefresh text.')
                break