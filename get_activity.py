import requests
# from urllib.parse import unquote
from u033_tools import colored_opt
from typing import Dict,Tuple
import re
import json

class fetch:
    """
    get父类，封装了点对超星客制化的功能
    """
    def __init__(self,headers_path,source_url,backend_api,*args) -> None:
        """
        父类请求函数
        Args:
            headers_path(str): 头部请求记录文件，当前版本data数据也写进header记录中了
            source_url(str): 请求域名url，如：`https://example.com`
            backend_api(str): 请求接口路径，如：`/api/xxx`
        
        """
        self.source_url = source_url
        self.backend_api = backend_api
        self.connect_code = -1
        self.response_text = ""
        self.cookies = self.split_cookies(open("headFolder/cookies.txt","r",encoding="utf8").read())
        self.c_mgr = colored_opt()
        self.session = requests.session()
        if not args :
            self.headers,self.request_data = self.read_head_file(headers_path)

    # TODO:分离headers和data
    def read_head_file(self,file_path:str)  -> Tuple[Dict[str,str],str]:
        """
        读取文件，返回字典和data
        Args:
            file_path(str): 文件路径
        Returns:
            Tuple:
                - headers: 请求头
                - data: 请求data
        """
        def split_lines(line:str) -> tuple:
            index = line.find(":")
            assert index,'未找到":"'
            key = line[:index]
            value = line[index+2:]
            return (key,value)
        headers:Dict[str,str] = {}
        request_data:str = ""
        with open(file_path,'r') as headers_f:

            while True:
                header_option = headers_f.readline().strip()
                if not header_option : break
                k_v = split_lines(header_option)
                if k_v[0] == "data":
                    request_data = k_v[1]
                else:
                    headers[k_v[0]] = k_v[1]
        return (headers,request_data)

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
        requests_data = self.request_data
        
        for k,v in self.headers.items():
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
        super().__init__("headFolder/activity_headers.txt",'https://hd.chaoxing.com','/hd/api/activity/list/participate')
        self.json = self.get_activity_json()

    def get_activity_json(self) -> str:
        """
        获取当前课程列表
        """
        request_url = self.source_url + self.backend_api
        chaoxing_response = self.session.post(request_url,
                                              headers=self.headers
                                              ,data=self.request_data,
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
        super().__init__("headFolder/activity_html_headers.txt",
                         f"https://{sub_domain}.mh.chaoxing.com",
                         f"/entry/page/{page_id}/show")
        self.raw_html = self._get_html()
    def _get_html(self):
        url = self.source_url + self.backend_api
        response = self.session.get(url,
                        headers=self.headers,
                        cookies=self.cookies,
                        )
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
        super().__init__("headFolder/domain_activity_information_headers.txt", "https://hd.chaoxing.com", f"/hd/activity/{class_id}")
        self.domain = self._get_domain()
    def _get_domain(self) -> str:
        """
        获取302重定向之后的url中的最后一级域名名称，通常为8位字母+数字组合
        Returns:
            str: 8位字母+数字组合
        """
        url = self.source_url + self.backend_api
        response = self.session.get(url,
                            headers=self.headers,
                            cookies=self.cookies,
                            allow_redirects=False,
                            )
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
        super().__init__("headFolder/activity_information_headers.txt", "https://api.hd.chaoxing.com", "/mh/v3/activity/info")
        self.page_id = page_id
        self.website_id = website_id
        self.sub_domain = sub_domain
        self.json = self._get_json()
    def _get_json(self):
        tmp = self.headers["Origin"][:8] + self.sub_domain + self.headers["Origin"][16:]
        url = self.source_url + self.backend_api
        self.headers["Origin"] = tmp
        self.headers["Referer"] = tmp + "/"
        self.request_data = json.loads(self.request_data)
        self.request_data["pageId"] = self.page_id
        self.request_data["websiteId"] = self.website_id
        session = requests.session()
        response = session.post(url,
                     headers=self.headers,
                     cookies=self.cookies,
                     json=self.request_data)
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.json()

class get_activity_describe(fetch):
    """用于获取课程描述信息"""
    def __init__(self, page_id,website_id,wfwfid) -> None:
        """
        获取描述信息
        Args:
            page_id: 课程列表中的pageId
            website_id: 课程列表中的websiteId
            wfwfid: HTML结构中的p_wfwfid变量值
        """
        super().__init__("headFolder/describe_headers.txt",
                         "https://hd.chaoxing.com",
                         f"/api/activity/introduction?pageId={page_id}&current_pageId={page_id}&current_websiteId={website_id}&current_wfwfid={wfwfid}")
        self.describe = self._get_describe()
    def _get_describe(self):
        url = self.source_url + self.backend_api
        response = self.session.post(url,
                     headers=self.headers,
                     json=self.request_data)
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
        super().__init__("headFolder/css_file_headers.txt"," https://pc.chaoxing.com","/res/css/subscribe/pop.css?v=4")
        self.sub_domain = sub_domain

        self.css = self._get_css() 
    def _get_css(self):
        url = self.source_url + self.backend_api
        tmp = self.headers["Referer"][:8] + self.sub_domain + self.headers["Referer"][16:]
        self.headers["Referer"] = tmp
        # self.headers["If-Modified-Since"] = ""
        response = self.session.get(url,
                        headers=self.headers,
                        cookies=self.cookies,
                        )
        self.connect_code = response.status_code
        self.response_text = response.text
        self.session.close()
        return response.text
    


if __name__ == "__main__":
    # For test. qwq
    test_target = 5
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
        test = get_activity_detial(2305690,950312,"5o9skajr")
        print(test.get_info())
        print(test.json)
    elif test_target == 4:
        test = get_activity_describe(2305690,950312,296090)
        print(test.get_info())
        print(test.describe)
    elif test_target == 5:
        test = get_css("5o9skajr")
        print(test.get_info())

