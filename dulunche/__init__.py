import dulunche.check_env
import asyncio
import random
import time
import queue
import logging
import requests
import http.cookiejar as cookielib

from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from dulunche.danmaku import Danmaku, DanmakuList
from dulunche.biliapi import BiliLiveAPI
from dulunche.dmc import DanmakuClient
from dulunche.login import bzlogin

class AutoDuLunChe():
    def __init__(self, 
                 room_id,
                 cookies, 
                 check_length=60, 
                 min_freq=1,
                 interval=15,
                 random_size=3,
                 filter_medal=True,
                 filter_self=True,
                 **kwargs) -> None:
        self.room_id = room_id
        self.check_length = check_length
        self.min_freq = min_freq
        if not isinstance(interval, dict):
            self.interval = {0:float(interval)}
        else:
            self.interval = interval
        self.random_size = random_size
        self.filter_medal = filter_medal
        self.filter_self = filter_self
        self.kwargs = kwargs

        while 1:
            if isinstance(cookies, str):
                cookies = cookielib.LWPCookieJar(filename=cookies)
                cookies.load(ignore_discard=True)
                cookies = requests.utils.dict_from_cookiejar(cookies)
            self.cookies = cookies
            self.bapi = BiliLiveAPI(cookies=self.cookies)
            login_info = self.bapi.get_user_info(self.room_id)
            if login_info['code'] != 0:
                input('未登录，回车开始扫码登录:')
                bzlogin(self.cookies)
            else:
                data = login_info['data']
                self.up_medal = data['medal']['up_medal']['medal_name']
                self.uname = data['info']['uname']
                if data['medal']['is_weared']:
                    logging.info(f"正在使用账号 {data['info']['uname']} 独轮车，佩戴 {data['medal']['curr_weared']['medal_name']} {data['medal']['curr_weared']['level']}级 牌子.")
                else:
                    logging.info(f"正在使用账号 {data['info']['uname']} 独轮车，未戴牌子.")
                break
        
        self.dmlist = DanmakuList(duration=self.check_length)
        self.total_cnt = 0
        self.stoped = True

    def start_dmc(self):
        async def danmu_monitor():
            q = asyncio.Queue()
            self.dmc = DanmakuClient(url=f'https://live.bilibili.com/{self.room_id}', q=q)

            async def dmc_task():
                while not self.stoped:
                    try:
                        await self.dmc.start()
                    except asyncio.CancelledError:
                        await self.dmc.stop()
                    except Exception as e:
                        await self.dmc.stop()
                        logging.error(e)
                
            asyncio.create_task(dmc_task())
            
            while not self.stoped:
                dm = await q.get()
                if self.dmavailable(dm):
                    dm = Danmaku(
                        dmid=0,
                        dmtype=dm['msg_type'],
                        streamer=None,
                        sender=dm['name'],
                        stime=dm['time'],
                        content=dm['content'],
                        color=dm['color']
                    )
                    self.dmlist.add(dm)

        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        asyncio.get_event_loop().run_until_complete(danmu_monitor())

    def dmavailable(self, dm):
        if dm['msg_type'] in ['danmaku','emoticon']:
            medal = dm['raw_data']['info'][3]
            if self.filter_self and dm['name'] == self.uname:
                return False
            if self.filter_medal == 'medal':
                return bool(medal)
            elif self.filter_medal == 'fans':
                return bool(self.up_medal == medal[1])
            else:
                return True
        return False

    def start_sender(self):
        logging.info('正在收集弹幕数据...')
        time.sleep(self.check_length)

        while not self.stoped:
            num = len(self.dmlist)
            if num < self.check_length*self.min_freq:
                logging.info(f'弹幕过少，设置频率阈值 {self.min_freq}条/秒，实际发送速率 {num/self.check_length}条/秒，暂停开车.')
                time.sleep(self.check_length)
                continue
            top_danmu = self.dmlist.count(top=self.random_size)
            dm, _ = random.choice(top_danmu)

            try:
                rt = self.bapi.send_danmu(self.room_id, msg=dm.content, emoticon=int(dm.dmtype=='emoticon'))
                if rt['msg'] == '':
                    self.total_cnt += 1
                    logging.info(f'独轮车 {self.total_cnt:04d}: {dm.content} 发送成功.')
                else:
                    logging.error(f"独轮车 {dm.content} 发送失败, {rt['msg']}.")
                    time.sleep(5)
                    continue
            except Exception as e:
                logging.error(f'独轮车 {dm.content} 发送失败, {e}.')
                time.sleep(5)
                continue

            sleep_time = self.check_length
            for n, t in self.interval.items():
                if num/self.check_length > n:
                    sleep_time = t
            time.sleep(sleep_time)
        
    def start(self):
        self.stoped = False
        self.futures = []
        pool = ThreadPoolExecutor(max_workers=2)
        self.futures.append(pool.submit(self.start_dmc))
        self.futures.append(pool.submit(self.start_sender))
        for future in as_completed(self.futures):
            future.result()

    def stop(self):
        self.stoped = True


