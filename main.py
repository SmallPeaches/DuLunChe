import argparse
import os
import re
import time
from sender.biliapi import BiliLiveAPI

def read_text(fpath,mode):
    text = []

    if mode == 'dulunche':
        with open(fpath,'r',encoding='utf-8') as f:
            text_list = f.readlines()
            for t in text_list:
                t = t.strip()
                t = re.sub(r"[\n,，.。～！、;；]",' ',t)
                if len(t) > 0:
                    text.append(t[:30])
    else:
        with open(fpath,'r',encoding='utf-8') as f:
            text_list = f.read().replace(' ','')
            str_list = re.split(r"[\n,，.。～！、;；]",text_list)
            str_list = [s for s in str_list if s and len(s.strip())>0]
            p = 0
            while p < len(str_list):
                t = str_list[p]
                if len(t) < 10:
                    while p < len(str_list)-1 and len(t+' '+str_list[p+1]) < 25:
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

def get_mode(fpath):
    with open(fpath,'r',encoding='utf-8') as f:
        text_list = f.readlines()
        sen_max = max([len(x) for x in text_list])
        if sen_max > 40:
            mode = 'shuoshu'
        else:
            mode = 'dulunche'
    return mode 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookiespath',type=str,default='./cookies.txt')
    parser.add_argument('--rid',type=str,default='23197314')
    parser.add_argument('--txtpath',type=str,default='./text.txt')
    parser.add_argument('--interval',type=float,default=20)
    parser.add_argument('--mode',choices=['auto','shuoshu','dulunche'],default='auto')
    args = parser.parse_args()

    if args.mode == 'auto':
        args.mode = get_mode(args.txtpath)
    text = read_text(args.txtpath,mode=args.mode)
    mode = '独轮车' if args.mode == 'dulunche' else '说书'

    print(f'{mode}总数{len(text)}, 间隔{args.interval}sec.')

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

            new_text = read_text(args.txtpath,mode=args.mode)
            if new_text != text:
                text = new_text
                print('refresh text.')
                break
            continue

        for word_cnt,txt in enumerate(text):
            if txt.startswith('#') and not txt.startswith('##'):
                txt = txt[1:]
                emoticon = 1
                mode = '表情独轮车'
            else:
                if txt.startswith('##'):
                    txt = txt[1:]
                emoticon = 0
            rt = sender.send_danmu(args.rid,txt,emoticon=emoticon)
            dm_cnt += 1
            if rt['msg'] != '':
                kill_cnt += 1
                print(f'{mode} {word_cnt+1}/{len(text)} was killed ({rt["msg"]}): {txt}.')
                time.sleep(5)
            else:
                print(f'{mode} {word_cnt+1}/{len(text)}, total {dm_cnt:04d}: {txt}.')
                time.sleep(args.interval)

            new_text = read_text(args.txtpath,mode=args.mode)
            if new_text != text:
                text = new_text
                print('Refresh text...')
                break