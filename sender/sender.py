from sender.biliapi import BiliLiveAPI
from antishield.BiliLiveShieldWords import rules,words
from antishield.BiliLiveAntiShield import BiliLiveAntiShield

class Sender():
    def __init__(self,cookies,rid,antishield_mode='no') -> None:
        self.bapi = BiliLiveAPI(cookies=cookies)
        if self.bapi.get_room_info(rid)['code'] != 0:
            raise ValueError(f'直播间{rid}错误！')
        if antishield_mode != 'no':
            self.bilishield = BiliLiveAntiShield(rules,words,"`")
        self.rid = rid
        self.antishield_mode = antishield_mode

    def send(self,msg,return_msg=False):
        if self.antishield_mode == 'all':
            msg = self.bilishield.deal(msg)

        rval = self.bapi.send_danmu(self.rid,msg=msg)
        if return_msg:
            return rval,msg
        else:
            return rval

    def sendx(self,msg:str):
        if msg.startswith('#') and not msg.startswith('##'):
            msg = msg[1:]
            emoticon = 1
        else:
            if msg.startswith('##'):
                msg = msg[1:]
            emoticon = 0

        rt = self.bapi.send_danmu(self.rid,msg=msg,emoticon=emoticon)

        if rt.get('msg') is None:
            raise RuntimeError('登陆错误! 请运行python login.py重新登录.')
        elif rt.get('msg') == '':
            return True,''
        else:
            return False,rt['msg']
