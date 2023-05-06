import threading
from datetime import datetime, timedelta

class Danmaku(dict):
    def __init__(
        self,
        dmid:int,
        dmtype:str,
        streamer:str,
        sender:str,
        stime:datetime,
        content:str,
        color:str
    ) -> None:
        super().__init__()
        self['dmid'] = dmid
        self['dmtype'] = dmtype
        self['streamer'] = streamer
        self['sender'] = sender
        self['stime'] = stime
        self['content'] = content
        self['color'] = color

    def __getattribute__(self, __name: str):
        try:
            return super().__getattribute__(__name)
        except AttributeError:
            return self[__name]
        
class DanmakuList():
    def __init__(self, duration=60) -> None:
        self.duration = duration
        self.lock = threading.Lock()
        self.dmlist = []
    
    def refresh(self):
        t0 = datetime.now() - timedelta(seconds=self.duration)
        while len(self.dmlist) > 0:
            if self.dmlist[0].stime < t0:
                with self.lock:
                    self.dmlist.pop(0)
            else:
                break
    
    def add(self, danmu):
        self.refresh()
        with self.lock:
            self.dmlist.append(danmu)

    def __len__(self):
        self.refresh()
        return len(self.dmlist)
    
    def count(self, top=0, type='all') -> dict:
        """
        return: List[tuple(Danmaku, cnt),...]
        """
        self.refresh()
        res = {}
        with self.lock:
            for dm in self.dmlist:
                if type == 'all' or type == dm.dmtype:
                    k = dm.content
                    if not res.get(k):
                        res[k] = (1, dm)
                    else:
                        res[k] = (res[k][0]+1, dm)
        
        res = sorted(res.items(), key=lambda x: x[1][0], reverse=True)
        if top>0:
            res = res[:top]
        res = [(it[1][1],it[1][0]) for it in res]
        return res

