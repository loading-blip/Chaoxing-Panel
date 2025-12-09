from typing import override,Iterator,Tuple
from urllib.parse import unquote,quote
import json

#################################
#   此文件内存放请求头，请求体
#   此文档class命名为获取到的内容含义
#   使用dict()对此文档里的类
#   都可以被显式转换
################################

class Headers:
    def __init__(self) -> None:
        self.Accept = "*/*"
        self.AcceptLanguage = "zh-CN,zh-Hans;q=0.9"
        self.AcceptEncoding = "gzip, deflate, br"
        self.UserAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 26_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 (schild:aea56116213a0e59888a2fc6e412afe0) (device:iPhone14,7) Language/zh-Hans com.ssreader.ChaoXingStudy/ChaoXingStudy_3_6.7.1_ios_phone_202511102025_311 (@Kalimdor)_3686988458511932094"

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        yield ('Accept',self.Accept)
        yield ('Accept-Language',self.AcceptLanguage)
        yield ('Accept-Encoding',self.AcceptEncoding)
        yield ('User-Agent',self.UserAgent)

class Datas:
    def __init__(self) -> None:
        self._data = {}
        
    def load_str(self,string,encode='raw') -> None:
        if encode=="raw":
            tmp = string
        elif encode == "utf8":
            tmp = unquote(string)
        else:
            raise TypeError("Unkonwn type:"+encode)
        self._data = json.loads(tmp)

    def get_data(self,endcode='raw') -> str:
        tmp = json.dumps(self._data)
        if endcode == "utf8":
            return quote(tmp)
        return tmp
    
    def get_json(self) ->dict:
        return self._data
    
    def set_data(self,data_dict:dict):
        self._data = data_dict

    def set_value(self,k,v) ->None :...
    
    def __iter__(self):
        return iter(self._data.items())

class activity_list(Headers):
    def __init__(self,UID) -> None:
        super().__init__()
        self.Host = "hd.chaoxing.com"
        self.XRequestedWith = "XMLHttpRequest"
        self.SecFetchSite = "same-origin"
        self.SecFetchMode = "cors"
        self.ContentType = "application/x-www-form-urlencoded; charset=UTF-8"
        self.Origin = "https://hd.chaoxing.com"
        self.ContentLength = "541"
        # TODO:待破译
        self.Referer = f"https://hd.chaoxing.com/?flag=second_classroom&fidEnc=12f635a11338a4b0&uid={UID}&mappId=19057374&mappIdEnc=32ae5a00fe3a9c3fe6e34473111170bf&wfwEnc=CCB9D82B85B74FE131B6DA29FC20C49A&appId=5c82b79ed26f4faa9654d49defe70f03&appKey=I86VRi1pp54zM1Ih&code=1Tk8Y1xS&state=296090"
        self.Connection = "keep-alive"
        self.SecFetchDest = "empty"

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('X-Requested-With',self.XRequestedWith)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Content-Type',self.ContentType)
        yield ('Origin',self.Origin)
        yield ('Content-Length',self.ContentLength)
        yield ('Referer',self.Referer)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class activity_sub_domain(Headers):
    def __init__(self) -> None:
        super().__init__()
        self.Host = "hd.chaoxing.com"
        self.SecFetchSite = "none"
        self.Connection = "keep-alive"
        self.SecFetchMode = "navigate"
        # TODO:待破译
        self.Referer = "https://hd.chaoxing.com/?flag=second_classroom&fidEnc=12f635a11338a4b0&uid=242075141&mappId=19057374&mappIdEnc=32ae5a00fe3a9c3fe6e34473111170bf&wfwEnc=7B01489A3E101ADC301C6C828125DB99&appId=5c82b79ed26f4faa9654d49defe70f03&appKey=I86VRi1pp54zM1Ih&code=06CRmeX8&state=296090"
        self.SecFetchDest = "document"

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Referer',self.Referer)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class activity_HTML(Headers):
    def __init__(self,sub_domain) -> None:
        super().__init__()
        self.Host = sub_domain + ".mh.chaoxing.com"
        self.SecFetchSite = "none"
        self.Connection = "keep-alive"
        self.SecFetchMode = "navigate"
        self.Referer = "https://hd.chaoxing.com/"
        self.SecFetchDest = "document"
    
    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Referer',self.Referer)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class activity_information(Headers):
    def __init__(self,sub_domain) -> None:
        super().__init__()
        self.Host = "api.hd.chaoxing.com"
        self.SecFetchSite = "same-site"
        self.SecFetchMode = "cors"
        self.ContentType = "application/json;charset=UTF-8"
        self.Origin = f"https://{sub_domain}.mh.chaoxing.com"
        self.Referer = f"https://{sub_domain}.mh.chaoxing.com/"
        self.ContentLength = "379"
        self.Connection = "keep-alive"
        self.SecFetchDest = "empty"

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Content-Type',self.ContentType)
        yield ('Origin',self.Origin)
        yield ('Referer',self.Referer)
        yield ('Content-Length',self.ContentLength)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class activity_describe(Headers):
    def __init__(self,sub_domain) -> None:
        super().__init__()
        self.Host = "hd.chaoxing.com"
        self.Origin = f"https://{sub_domain}.mh.chaoxing.com"
        self.Connection = "keep-alive"
        self.SecFetchMode = "cors"
        self.SecFetchSite = "same-site"
        self.Referer = f"https://{sub_domain}.mh.chaoxing.com/"
        self.SecFetchDest = "empty"

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('Origin',self.Origin)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Referer',self.Referer)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class activity_css(Headers):
    def __init__(self,sub_domain) -> None:
        super().__init__()
        self.Host = "pc.chaoxing.com"
        self.SecFetchSite = "same-site"
        self.SecFetchMode = "no-cors"
        self.Connection = "keep-alive"
        self.Referer = f"https://{sub_domain}.mh.chaoxing.com/"
        self.SecFetchDest = "style"

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Connection',self.Connection)
        yield ('Referer',self.Referer)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)

class account_cookies(Headers):
    def __init__(self) -> None:
        super().__init__()
        self.secchua = "?0"
        self.secchuaplatform = '"Windows"'

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('sec-ch-ua',self.secchua)
        yield ('sec-ch-ua-platform',self.secchuaplatform)

class activity_type(Headers):
    def __init__(self,UID) -> None:
        super().__init__()
        self.Host = 'hd.chaoxing.com'
        self.XRequestedWith = 'XMLHttpRequest'
        self.SecFetchSite = 'same-origin'
        self.SecFetchMode = 'cors'
        self.ContentType = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.Origin = 'https://hd.chaoxing.com'
        self.ContentLength = '109'
        self.Connection = 'keep-alive'
        self.SecFetchDest = 'empty'
        self.Referer = f'https://hd.chaoxing.com/second-classroom/result?fidEnc=12f635a11338a4b0&uid={UID}&mappId=19057375&mappIdEnc=d7a3b91b7fd8fa43f363477f220e1829&wfwEnc=C8DCDC5DB460151F998849FC72FEDABC&appId=881d2ff10f874628a8ba7acd577fd54c&appKey=nyDE2p13PU42yab5&code=PJa89eVa&state=296090'

    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('X-Requested-With',self.XRequestedWith)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Content-Type',self.ContentType)
        yield ('Origin',self.Origin)
        yield ('Content-Length',self.ContentLength)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)
        yield ('Referer',self.Referer)

class activity_record(Headers):
    def __init__(self,UID) -> None:
        super().__init__()
        self.Host = 'hd.chaoxing.com'
        self.XRequestedWith = 'XMLHttpRequest'
        self.SecFetchSite = 'same-origin'
        self.SecFetchMode = 'cors'
        self.ContentType = 'application/x-www-form-urlencoded; charset=UTF-8'
        self.Origin = 'https://hd.chaoxing.com'
        self.ContentLength = '120'
        self.Connection = 'keep-alive'
        self.SecFetchDest = 'empty'
        self.Referer = f'https://hd.chaoxing.com/second-classroom/result?fidEnc=12f635a11338a4b0&uid={UID}&mappId=19057375&mappIdEnc=d7a3b91b7fd8fa43f363477f220e1829&wfwEnc=C8DCDC5DB460151F998849FC72FEDABC&appId=881d2ff10f874628a8ba7acd577fd54c&appKey=nyDE2p13PU42yab5&code=PJa89eVa&state=296090'


    @override
    def __iter__(self):
        for item in super().__iter__():
            yield item
        yield ('Host',self.Host)
        yield ('X-Requested-With',self.XRequestedWith)
        yield ('Sec-Fetch-Site',self.SecFetchSite)
        yield ('Sec-Fetch-Mode',self.SecFetchMode)
        yield ('Content-Type',self.ContentType)
        yield ('Origin',self.Origin)
        yield ('Content-Length',self.ContentLength)
        yield ('Connection',self.Connection)
        yield ('Sec-Fetch-Dest',self.SecFetchDest)
        yield ('Referer',self.Referer)

class activity_list_data(Datas):
    def __init__(self,wfwid) -> None:
        super().__init__()
        self._data = {"pageNum": 1,
                    "pageSize": 10,
                    "sw": "",
                    "activityClassifyIds": [],
                    "dateScope": "",
                    "status": "",
                    "activityType": "",
                    "areaCode": None,
                    "topFid": wfwid,
                    "marketIds": [
                        25239
                    ],
                    "scope": None,
                    "flag": "second_classroom",
                    "signUpAble": False,
                    "entered": True,
                    "customFilterMap": {},
                    "customMultiValueFilterMap": {},
                    "orderType": "DESC",
                    "orderField": "DEFAULT"
                    }

class activity_information_data(Datas):
    def __init__(self) -> None:
        super().__init__()
        self._data = {
            "preParams": None,
            "pageSize": None,
            "pageId": 0,  # FILL
            "uid": "242075141",
            "page": 1,
            "classifies": [],
            "isMobile": True,
            "wfwfid": 0, # FILL
            "websiteId": 0, # FILL
            "vc3": "", # FILL
            "_d": "" # FILL
        }
    
    @override
    def set_value(self,k,v):
        if k in self._data.keys():
            self._data[k] = v
        else:
            raise NameError("Key Error",k)
        
class activity_type_data(Datas):
    def __init__(self,UID,realName,wfwfid) -> None:
        super().__init__()
        self._data = f"uid={UID}&realName={quote(realName)}&fid={wfwfid}&inspectionPlanId=159&schoolYear=&orgConfigId=91"

    @override
    def get_data(self, endcode='raw') -> str:
        if endcode == "utf8":
            return quote(self._data)
        return self._data
    
    @override
    def get_json(self) ->dict:
        raise ValueError('Please use get_data to get string Datas')

    def __str__(self) -> str:
        return self.get_data()

class activity_record_data(Datas):
    def __init__(self,UID,wfwfid) -> None:
        super().__init__()
        self._data = f"uid={UID}&fid={wfwfid}&inspectionPlanId=159&credit=&timeOrder=DESC&pageNum=1&pageSize=10000&schoolYear=&orgConfigId=91"

    @override
    def get_data(self, endcode='raw') -> str:
        if endcode == "utf8":
            return quote(self._data)
        return self._data
    
    @override
    def get_json(self) ->dict:
        raise ValueError('Please use get_data to get string Datas')
    
    def __str__(self) -> str:
        return self.get_data()