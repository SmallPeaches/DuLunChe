import argparse
import os
import re
import time
import requests
import http.cookiejar as cookielib
from dulunche.biliapi import BiliLiveAPI
from dulunche.login import bzlogin

def read_text(fpath,mode):
    text = []

    if '独轮车' in mode:
        with open(fpath,'r',encoding='utf-8') as f:
            text_list = f.readlines()
            for t in text_list:
                t = t.strip()
                # t = re.sub(r"[\n,，.。～！、;；]",' ',t)
                if len(t) > 0 and not t.startswith('//'):
                    text.append(t[:30])
                if t == '//':
                    break
    else:
        with open(fpath,'r',encoding='utf-8') as f:
            text_list = f.readlines()
            for line in text_list:
                line = line.strip()
                if line == '//':
                    break
                str_list = re.split(r"[,，.。～！、;；]",line)
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
            mode = '说书'
        else:
            mode = '独轮车'
    return mode 

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--cookies',type=str,default='./cookies.txt')
    parser.add_argument('-r','--rid',type=str,default='23197314')
    parser.add_argument('-t','--txt',type=str,default='./text.txt')
    parser.add_argument('-i','--interval',type=float,default=10)
    parser.add_argument('--mode',choices=['auto','shuoshu','dulunche'],default='auto')
    args = parser.parse_args()

    if args.mode == 'auto':
        args.mode = get_mode(args.txt)
    mode = '独轮车' if args.mode == 'dulunche' else '说书'
    text = read_text(args.txt,mode=args.mode)

    while 1:
        if isinstance(args.cookies, str):
            cookies = cookielib.LWPCookieJar(filename=args.cookies)
            cookies.load(ignore_discard=True)
            cookies = requests.utils.dict_from_cookiejar(cookies)
        else:
            cookies = args.cookies
        bapi = BiliLiveAPI(cookies=cookies)
        login_info = bapi.get_user_info(args.rid)
        if login_info['code'] != 0:
            input('未登录，回车开始扫码登录:')
            bzlogin(args.cookies)
        else:
            data = login_info['data']
            if data['medal']['is_weared']:
                print(f"正在使用账号 {data['info']['uname']} 独轮车，佩戴 {data['medal']['curr_weared']['medal_name']} {data['medal']['curr_weared']['level']}级 牌子.")
            else:
                print(f"正在使用账号 {data['info']['uname']} 独轮车，未戴牌子.")
            break
    
    dm_cnt = 0
    kill_cnt = 0
    
    while 1:
        if len(text) < 1:
            print('No text, waiting...')
            time.sleep(1)

            mode = get_mode(args.txt)
            new_text = read_text(args.txt,mode=mode)
            if new_text != text:
                text = new_text
                print('refresh text.')
                break
            continue

        for word_cnt,txt in enumerate(text):
            if txt.startswith('#') and not txt.startswith('##'):
                txt = txt[1:]
                mode = '表情独轮车'
            
            try:
                rt = bapi.send_danmu(roomid=args.rid,msg=txt,emoticon=int(mode=='表情独轮车'))
                if rt['msg'] == '':
                    status = True
                else:
                    status = False
                    msg = rt['msg']
            except Exception as e:
                print(e)
                continue
                
            dm_cnt += 1
            if status:
                print(f'{mode} {word_cnt+1}/{len(text)}, total {dm_cnt:04d}: {txt}.')
                time.sleep(args.interval)
            else:
                kill_cnt += 1
                print(f'{mode} {word_cnt+1}/{len(text)} was killed ({msg}): {txt}.')
                time.sleep(5)

            mode = get_mode(args.txt)
            new_text = read_text(args.txt,mode=mode)
            if new_text != text:
                text = new_text
                print('Refresh text...')
                break