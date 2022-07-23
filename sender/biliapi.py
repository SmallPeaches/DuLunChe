# -*- coding: utf-8 -*-

import getpass
import json
import requests
from http import cookiejar

import urllib

from datetime import datetime

# LOGIN PART
LOGIN_URL = 'https://passport.bilibili.com/ajax/miniLogin/minilogin'
LOGIN_HEADER = {
    'Host': 'passport.bilibili.com',
            'Referer': 'https://passport.bilibili.com/ajax/miniLogin/minilogin',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Connection': 'keep-alive',
            'Cache-Control': 'max-age=0',
            'Origin': 'https://passport.bilibili.com'
}
LOGIN_DATA = {
    'keep': 0,
    'captcha': ''
}

# LOGIN PART
SEND_URL = 'http://live.bilibili.com/msg/send'

SEND_FORMAT = {
    "color": "000000",
    "fontsize": "11",
    "mode": "1",
}

class SenderService(object):

    """提供弹幕发送服务。
    """

    def __init__(self, room_id):
        """初始化服务。
        :params: room_id: 直播间号。
        """
        self.session = requests.Session()
        # 设置cookie
        self.cookie = cookiejar.CookieJar()
        cookie_handler = urllib.request.HTTPCookieProcessor(self.cookie)
        self.opener = urllib.request.build_opener(
            cookie_handler, urllib.request.HTTPHandler)
        self.send_danmaku(room_id)

    def send_danmaku(self, room_id):
        """发送弹幕。
        :params: room_id: 直播间号。
        """
        self.do_login()
        self.danmaku_sender(room_id)

    def do_login(self):
        # 载入登陆设置
        self._pre_login()
        # 获取 登陆必要参数
        while 1:
            user_id = input('请输入你的用户名：')
            password = getpass.getpass('请输入你的密码：')
            # 进行登录
            if not self._login(user_id, password):
                continue

    def _pre_login(self):
        """进行登录前信息配置信息。"""
        # 将页面信息加入头部
        req = urllib.request.Request(LOGIN_URL)
        resp = self.opener.open(req)
        self.login_header = LOGIN_HEADER
        for i in self.cookie:
            self.login_header['Cookie'] = i.name + '=' + i.value

    def _login(self, user_id, password):
        """登陆操作。

        :params: user_id: 用户账户或邮箱。
        :params: password: 密码。
        """
        data = LOGIN_DATA
        data['userid'] = user_id
        data['pwd'] = password
        response = self.session.post(
            'https://account.bilibili.com/ajax/miniLogin/login',
            data=data,
            headers=self.login_header
        )
        if not response.json()['status']:
            print ("输入的用户名或密码有误！")
            return False
        # response.raise_for_status()
        self.cookie = response.cookies
        return True

    def danmaku_sender(self, room_id):
        """不断发送弹幕。
        :params: room_id: 直播间号。
        """
        print ("准备开启弹幕发射！")
        while True:
            try:
                danmaku = input('输入发送的弹幕(Exit 退出)：')
                if danmaku.lower() == "exit":
                    break
            except KeyboardInterrupt:
                break
            except:
                continue
            self.send_a_danmaku(room_id, danmaku)

    def send_a_danmaku(self, room_id, danmaku):
        """发送一条弹幕。
        :params: room_id: 直播间号。
        :params: danmaku: 弹幕信息。
        """

        data = SEND_FORMAT
        data["msg"] = danmaku
        data["roomid"] = room_id
        json_data = json.dumps(data)
        response = self.session.post(
            SEND_URL,
            data=data,
            cookies=self.cookie
        )
        response.raise_for_status()
        if response.json().get('code') == 0:
            print ("弹幕已发出")
        else:
            print (response.json().get('msg'))
        return True

import json
import re
import time
from typing import List, Union
import requests

class BaseAPI:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.63 Safari/537.36 Edg/102.0.1245.30",
    }
    def __init__(self,timeout=(3.05,5)):
        self.timeout=timeout
        
    
    def set_default_timeout(self,timeout=(3.05,5)):
        self.timeout=timeout

class BiliLiveAPI(BaseAPI):
    def __init__(self,cookies:Union[List[str],str],timeout=(3.05,5)):
        """B站直播相关API"""
        super().__init__(timeout)
        self.headers = dict(self.headers,
            Origin="https://live.bilibili.com",
            Referer="https://live.bilibili.com/")
        self.sessions = []
        self.csrfs = []
        self.rnd=int(time.time())
        if isinstance(cookies,str):    cookies=[cookies]
        for i in range(len(cookies)):
            self.sessions.append(requests.session())
            self.csrfs.append("")
            self.update_cookie(cookies[i],i)
    
    def get_room_info(self,roomid,timeout=None) -> dict:
        """获取直播间标题、简介等信息"""
        url="https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByRoom"
        params={"room_id":roomid}
        if timeout is None: timeout=self.timeout
        res=requests.get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)

    def get_danmu_config(self,roomid,number=0,timeout=None) -> dict:
        """获取用户在直播间内的可用弹幕颜色、弹幕位置等信息"""
        url="https://api.live.bilibili.com/xlive/web-room/v1/dM/GetDMConfigByGroup"
        params={"room_id":roomid}
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)
    
    def get_user_info(self,roomid,number=0,timeout=None) -> dict:
        """获取用户在直播间内的当前弹幕颜色、弹幕位置、发言字数限制等信息"""
        url="https://api.live.bilibili.com/xlive/web-room/v1/index/getInfoByUser"
        params={"room_id":roomid}
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)
    
    def set_danmu_config(self,roomid,color=None,mode=None,number=0,timeout=None) -> dict:
        """设置用户在直播间内的弹幕颜色或弹幕位置
        :（颜色参数为十六进制字符串，颜色和位置不能同时设置）"""
        url="https://api.live.bilibili.com/xlive/web-room/v1/dM/AjaxSetConfig"
        data={
            "room_id": roomid,
            "color": color,
            "mode": mode,
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def send_danmu(self,roomid,msg,mode=1,number=0,timeout=None) -> dict:
        """向直播间发送弹幕"""
        url="https://api.live.bilibili.com/msg/send"
        data={
            "color": 16777215,
            "fontsize": 25,
            "mode": mode,
            "bubble": 0,
            "msg": msg,
            "roomid": roomid,
            "rnd": self.rnd,
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def get_slient_user_list(self,roomid,number=0,timeout=None):
        """获取房间被禁言用户列表"""
        url="https://api.live.bilibili.com/xlive/web-ucenter/v1/banned/GetSilentUserList"
        params={
            "room_id": roomid,
            "ps": 1,
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)
    
    def add_slient_user(self,roomid,uid,number=0,timeout=None):
        """禁言用户"""
        url="https://api.live.bilibili.com/xlive/web-ucenter/v1/banned/AddSilentUser"
        data={
            "room_id": roomid,
            "tuid": uid,
            "mobile_app": "web",
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)

    def del_slient_user(self,roomid,silent_id,number=0,timeout=None):
        """解除用户禁言"""
        url="https://api.live.bilibili.com/banned_service/v1/Silent/del_room_block_user"
        data={
            "roomid": roomid,
            "id": silent_id,
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def get_shield_keyword_list(self,roomid,number=0,timeout=None):
        """获取房间屏蔽词列表"""
        url="https://api.live.bilibili.com/xlive/web-ucenter/v1/banned/GetShieldKeywordList"
        params={
            "room_id": roomid,
            "ps": 2,
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)

    def add_shield_keyword(self,roomid,keyword,number=0,timeout=None):
        """添加房间屏蔽词"""
        url="https://api.live.bilibili.com/xlive/web-ucenter/v1/banned/AddShieldKeyword"
        data={
            "room_id": roomid,
            "keyword": keyword,
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def del_shield_keyword(self,roomid,keyword,number=0,timeout=None):
        """删除房间屏蔽词"""
        url="https://api.live.bilibili.com/xlive/web-ucenter/v1/banned/DelShieldKeyword"
        data={
            "room_id": roomid,
            "keyword": keyword,
            "csrf_token": self.csrfs[number],
            "csrf": self.csrfs[number],
        }
        if timeout is None: timeout=self.timeout
        res=self.sessions[number].post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def search_live_users(self,keyword,page_size=10,timeout=None) -> dict:
        """根据关键字搜索直播用户"""
        url="https://api.bilibili.com/x/web-interface/search/type"
        params={
            "keyword": keyword,
            "search_type": "live_user",
            "page_size": page_size,
        }
        if timeout is None: timeout=self.timeout
        res=requests.get(url=url,headers=self.headers,params=params,timeout=timeout)
        return json.loads(res.text)
    
    def get_login_url(self,timeout=None):
        """获取登录链接"""
        url="https://passport.bilibili.com/qrcode/getLoginUrl"
        if timeout is None: timeout=self.timeout
        res=requests.get(url=url,headers=self.headers,timeout=timeout)
        return json.loads(res.text)
    
    def get_login_info(self,oauthKey,timeout=None):
        """检查登录链接状态，获取登录信息"""
        url="https://passport.bilibili.com/qrcode/getLoginInfo"
        data={
            "oauthKey": oauthKey,
        }
        if timeout is None: timeout=self.timeout
        res=requests.post(url=url,headers=self.headers,data=data,timeout=timeout)
        return json.loads(res.text)
    
    def update_cookie(self,cookie:str,number=0) -> str:
        """更新账号Cookie信息
        :返回cookie中buvid3,SESSDATA,bili_jct三项的合并内容"""
        cookie = re.sub(r"\s+", "", cookie)
        mo1 = re.search(r"buvid3=([^;]+)", cookie)
        mo2 = re.search(r"SESSDATA=([^;]+)", cookie)
        mo3 = re.search(r"bili_jct=([^;]+)", cookie)
        buvid3,sessdata,bili_jct=mo1.group(1) if mo1 else "",mo2.group(1) if mo2 else "",mo3.group(1) if mo3 else ""
        cookie="buvid3=%s;SESSDATA=%s;bili_jct=%s"%(buvid3,sessdata,bili_jct)
        requests.utils.add_dict_to_cookiejar(self.sessions[number].cookies,{"Cookie": cookie})
        self.csrfs[number]=bili_jct
        return cookie

class JsdelivrAPI(BaseAPI):
    def __init__(self, timeout=(6.05,5)):
        """Jsdelivr公共CDN的API"""
        super().__init__(timeout)

    def get_latest_bili_live_shield_words(self,domain="cdn",timeout=None) -> str:
        """获取最新的B站直播屏蔽词处理脚本（Github项目：FHChen0420/bili_live_shield_words）"""
        url=f"https://{domain}.jsdelivr.net/gh/FHChen0420/bili_live_shield_words@main/BiliLiveShieldWords.py"
        if timeout is None: timeout=self.timeout
        res=requests.get(url,headers=self.headers,timeout=timeout)
        return res.text

if __name__ == '__main__':
    cookies = ''    
    bapi = BiliLiveAPI(cookies=cookies)
    rid = '23197314'
    res = bapi.send_danmu(rid,'test, from python')
    bapi.get_shield_keyword_list(rid)
    a = 1