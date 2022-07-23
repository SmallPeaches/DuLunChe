from sender.biliapi import BiliLiveAPI
from antishield.BiliLiveShieldWords import rules,words
from antishield.BiliLiveAntiShield import BiliLiveAntiShield

class Sender():
    def __init__(self,cookies,rid,antishield_mode='no') -> None:
        self.bapi = BiliLiveAPI(cookies=cookies)
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
