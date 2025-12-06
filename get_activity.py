import requests
from u033_tools import colored_opt
import re
from request_info import *
from cipher import AESCipher
from config import Config

#####################################
#   此文件内存放各种页面的请求方法
#   每个类都有.get_info()用于调试
#   若需要增加新功能
#   新功能的请求代码段需要集中存放于此
#####################################


class fetch:
    """
    所有请求的父类，封装了点对超星客制化的功能
    """
    # HACK: 减少传参内容
    def __init__(self,headers_id:int,source_url:str,backend_api:str,datas_id=0,sub_domain="") -> None:
        """
        父类请求函数
        Args:
            headers_id(str): 头部请求记录文件，当前版本data数据也写进header记录中了
            source_url(str): 请求域名url，如：`https://example.com`
            backend_api(str): 请求接口路径，如：`/api/xxx`
            datas_id(int): 需要加载的data类
            sub_domain(str): 此请求需要的sub_domain
        """
        self.source_url = source_url
        self.backend_api = backend_api
        self.connect_code = -1
        self.response_text = ""
        self._config = Config()
        self.cookies = dict(get_cookies(self._config))
        self.c_mgr = colored_opt()
        self.headers_list = [
            activity_list(self.cookies['UID']),
            activity_sub_domain(),
            activity_HTML(sub_domain),
            activity_information(sub_domain),
            activity_describe(sub_domain),
            activity_css(sub_domain),
            account_cookies()
        ]
        self.datas_list = [
            Datas(),
            activity_list_data(self.cookies['wfwfid']),
            activity_information_data()
            ]
        self.headers = self.headers_list[headers_id]
        self.datas = self.datas_list[datas_id]
        self.session = requests.session()
        self.session.headers.update(dict(self.headers))
        self.session.cookies.update(self.cookies)

    def split_cookies(self,cookies:str) -> dict:
        """
        切割cookies
        Args:
            cookies(str): cookies字符串
        Returns:
            dict: 符合requests的字典dict
        """
        if not cookies:
            return {}
        cookie_dict = {}
        for part in cookies.split(';'):
            part = part.strip()
            if not part:
                continue
            if '=' in part:
                k, v = part.split('=', 1)
                cookie_dict[k.strip()] = v.strip()
            else:
                cookie_dict[part] = ''
        return cookie_dict
    # HACK：应该返回字典，现在的情况应该命名成print_info()
    def get_info(self) -> str:
        """
        简述当前请求
        Returns:
            str:返回响应
        """
        request_url = self.source_url + self.backend_api
        requests_head = []
        requests_data = self.datas
        
        for k,v in dict(self.headers).items():
            if len(v)>50:
                v = v[:48] + self.c_mgr.yellow + self.c_mgr.default + "..." + self.c_mgr.default
            requests_head.append(f"{self.c_mgr.blue}{k}{self.c_mgr.default}: {v}") 
        

        opt =[f"{self.c_mgr.purple}url{self.c_mgr.default}: {request_url}",
              f"{self.c_mgr.purple}headers{self.c_mgr.default}: \n\t{"\n\t".join(requests_head)}",
              f"{self.c_mgr.purple}data{self.c_mgr.default}: {requests_data}"]

        return "\n".join(opt)

class get_activity(fetch):
    """
    用于获取当前课程列表
    """
    def __init__(self):
        super().__init__(0,'https://hd.chaoxing.com','/hd/api/activity/list/participate',1)
        self.datas = "data=" + self.datas.get_data('utf8') + "&pageNum=1&pageSize=10"
        self.json = self.get_activity_json()

    def get_activity_json(self) -> str:
        """
        获取当前课程列表
        """
        request_url = self.source_url + self.backend_api
        chaoxing_response = self.session.post(request_url,
                                              data=self.datas,
                                              cookies=self.cookies)
        
        self.connect_code = chaoxing_response.status_code
        self.response_text = chaoxing_response.text
        self.session.close()
        return self.response_text

class get_activity_HTML(fetch):
    """
    用于获取当前课程HTML结构，但主要功能为获取wfwf_Id
    """
    def __init__(self, sub_domain:str,page_id) -> None:
        """
        获取wfwf_Id
        Args:
            sub_domain: 302重定向返回时的Location最后一级域名
            page_id: 课程中的pageId
        """
        super().__init__(2,
                         f"https://{sub_domain}.mh.chaoxing.com",
                         f"/entry/page/{page_id}/show",sub_domain=sub_domain)
        self.raw_html = self._get_html()
    def _get_html(self):
        url = self.source_url + self.backend_api
        response = self.session.get(url)
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.text
    def get(self,key):
        find_key= re.search(key+r'\s*=\s*(\d+)',self.raw_html)
        if find_key:
            key = find_key.group(1)
        else:
            raise ValueError(f"Cannot find key:{key} in response.")

        return key

class get_302_Location(fetch):
    """用于获取302重定向后指向的Location"""
    def __init__(self, class_id) -> None:
        """
        获取302重定向后指向的最后一级域名(报文头Location)
        Args:
            class_id: 每个课程的Id
        """
        super().__init__(1, "https://hd.chaoxing.com", f"/hd/activity/{class_id}")
        self.domain = self._get_domain()
    def _get_domain(self) -> str:
        """
        获取302重定向之后的url中的最后一级域名名称，通常为8位字母+数字组合
        Returns:
            str: 8位字母+数字组合
        """
        url = self.source_url + self.backend_api
        response = self.session.get(url,allow_redirects=False)
        domain = response.headers.get('Location')
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        if domain:
            return domain[8:16]
        else:
            raise BaseException("NetworkError","Cannot get subdomain")

class get_activity_detial(fetch):
    """用于获取课程详细信息"""
    def __init__(self,page_id,website_id,sub_domain) -> None:
        """
        获取课程报名开始与结束时间等详细信息
        Args:
            page_id: 课程列表中的pageId
            website_id: 课程列表中的websiteId
            sub_domain: 302重定向时的最后一级域名
        """
        super().__init__(3, "https://api.hd.chaoxing.com", "/mh/v3/activity/info",2,sub_domain=sub_domain)
        self.page_id = page_id
        self.website_id = website_id
        self.sub_domain = sub_domain
        self.json = self._get_json()
    def _get_json(self):
        url = self.source_url + self.backend_api
        self.datas.set("pageId",self.page_id)
        self.datas.set("websiteId",self.website_id)
        self.datas.set("wfwfid",self.cookies['wfwfid'])
        self.datas.set("vc3",self.cookies['vc3'])
        self.datas.set("_d",self.cookies['sso_t'])
        response = self.session.post(url,
                     json=dict(self.datas))
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.json()

class get_activity_describe(fetch):
    """用于获取课程描述信息"""
    def __init__(self, page_id,website_id) -> None:
        """
        获取描述信息
        Args:
            page_id: 课程列表中的pageId
            website_id: 课程列表中的websiteId
            wfwfid: HTML结构中的p_wfwfid变量值
        """
        super().__init__(4,
                         "https://hd.chaoxing.com",
                         f"/api/activity/introduction?pageId={page_id}&current_pageId={page_id}&current_websiteId={website_id}&current_wfwfid=")
        self.backend_api+=self.cookies['wfwfid']

        self.describe = self._get_describe()
    def _get_describe(self):
        url = self.source_url + self.backend_api
        response = self.session.post(url)
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.json()["data"]

class get_css(fetch):
    """用于获取描述那栏用的的css，非必要不获取\n已经缓存到根目录中了"""
    def __init__(self,sub_domain) -> None:
        """
        获取描述那栏用的的css
        Args:
            sub_domain: 302重定向时的最后一级域名
        """
        super().__init__(5," https://pc.chaoxing.com","/res/css/subscribe/pop.css?v=4",sub_domain=sub_domain)
        self.sub_domain = sub_domain

        self.css = self._get_css() 
    def _get_css(self):
        url = self.source_url + self.backend_api
        response = self.session.get(url)
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.text
    
class get_cookies:
    # 获取cookies的类需要独立父类
    def __init__(self,config_exam:Config) -> None:
        self._config = config_exam
        self.session = requests.session()
        self.cipher = AESCipher()
        self.url = "https://passport2.chaoxing.com/fanyalogin"
        self.headers = dict(account_cookies())
        self.data = {
            "fid": "-1",
            "uname": self.cipher.encrypt(self._config.user_name),
            "password": self.cipher.encrypt(self._config.password),
            "refer": "https%3A%2F%2Fi.chaoxing.com",
            "t": True,
            "forbidotherlogin": 0,
            "validate": "",
            "doubleFactorLogin": 0,
            "independentId": 0,
        }
        if self._config.use_cookies:
            cookies_file = open(self._config.cookies_file_path,'r',encoding='utf8')
            self.cookies = self.split_cookies(cookies_file.read())
        else:
            self.cookies = self._generate_cookies()
        
    def split_cookies(self,cookies:str) -> dict:
        """
        切割cookies
        Args:
            cookies(str): cookies字符串
        Returns:
            dict: 符合requests的字典dict
        """
        if not cookies:
            return {}
        cookie_dict = {}
        for part in cookies.split(';'):
            part = part.strip()
            if not part:
                continue
            if '=' in part:
                k, v = part.split('=', 1)
                cookie_dict[k.strip()] = v.strip()
            else:
                cookie_dict[part] = ''
        return cookie_dict
    
    def _generate_cookies(self) -> dict:
        resp = self.session.post(self.url, headers=self.headers, data=self.data)
        if resp and resp.json()["status"] == True:
            return dict(resp.cookies)
        else:
            raise EOFError("response failed")
    
    def debug(self):
        print(self.cookies)
    def __iter__(self):
        return iter(self.cookies.items())
        
if __name__ == "__main__":
    # For test. qwq
    test_target = 3
    if test_target == 0:
        test = get_activity()
        print(test.get_info())
        print(test.json)
    elif test_target == 1:
        test = get_activity_HTML("5o9skajr",2305690)
        print(test.get_info())
        print(test.raw_html)
        print(test.get("pageId"))
    elif test_target == 2:
        test = get_302_Location(4110881)
        print(test.get_info())
        print(test.domain)
    elif test_target == 3:
        test = get_activity_detial(2314590,952517,"5oy65hti")
        print(test.get_info())
        print(test.json)
    elif test_target == 4:
        test = get_activity_describe(2305690,950312)
        print(test.get_info())
        print(test.describe)
    elif test_target == 5:
        test = get_css("5o9skajr")
        print(test.get_info())
    elif test_target == 6:
        test =  get_cookies(Config())
        print(test.cookies)
