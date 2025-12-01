import requests
# from urllib.parse import unquote
from color import colored_opt
from typing import Dict,Tuple
import json

class get:
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
        self.cookies = {}
        self.source_url = source_url
        self.backend_api = backend_api
        self.connect_code = -1
        self.response_text = ""
        self.cookies = self.split_cookies(open("cookies.txt","r",encoding="utf8").read())
        self.c_mgr = colored_opt()
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

class get_activity(get):
    """
    用于获取当前课程列表
    """
    def __init__(self, *args):
        
        super().__init__("activity_headers.txt",'https://hd.chaoxing.com','/hd/api/activity/list/participate')


    def get_activity_json(self) -> str:
        """
        获取当前课程列表
        """
        request_url = self.source_url + self.backend_api
        get_session = requests.session()
        

        chaoxing_response = get_session.post(request_url,headers=self.headers,data=self.request_data,cookies=self.cookies)
        self.connect_code = chaoxing_response.status_code
        self.response_text = chaoxing_response.text
        get_session.close()
        return self.response_text

    
class get_activity_information(get):
    """
    用于获取每个课程的简述内容
    """
    def __init__(self, preview_url:str,page_id:int,website_id:int,*args) -> None:
        """
        构造简述内容，注意：运行完此构造函数就已经获取到内容了
        Args:
            preview_url(str): 是课程列表json每个课程的中的"previewUrl"
            page_id(int): 是课程列表json每个课程的中的"pageId"
            website_id(int): 是课程列表json每个课程的中的"websiteId"
        """
        self.preview_url = preview_url
        self.page_id = page_id
        self.website_id = website_id
        self.pre_request_headers = self.read_head_file("domain_activity_information_headers.txt")[0]
        
        super().__init__("activity_information_headers.txt","https://api.hd.chaoxing.com","/mh/v3/activity/info")
        # 获取简述需要Origin与Referer，这两个关键信息在此重定向的结果中获取
        self.sub_domain = self.get_domain()
        self.request_data = json.loads(self.request_data)
        self.request_data["pageId"] = page_id
        self.request_data["websiteId"] = website_id

        tmp = self.headers["Origin"][:8] + self.sub_domain + self.headers["Origin"][16:]
        self.headers["Origin"] = tmp
        self.headers["Referer"] = tmp + "/"
        self.json = self.get_json()
    def get_domain(self) -> str:
        """
        获取302重定向之后的url中的最后一级域名名称，通常为8位字母+数字组合
        Returns:
            str: 8位字母+数字组合
        """
        session = requests.session()
        domain = ""
        request = session.get(self.preview_url,
                    headers=self.pre_request_headers,
                    cookies=self.cookies,
                    allow_redirects=False,
                    timeout=(3,5))
        domain = request.headers.get('Location')
        if domain:
            return domain[8:16]
        else:
            raise BaseException("NetworkError","Cannot get subdomain")
    def get_json(self) -> dict:
        """
        获取活动详细信息
        Returns:
            dict:返回序列化后的json字典
            
        """
        url = self.source_url + self.backend_api
        session = requests.session()
        get_detial_json = session.post(url,
                     headers=self.headers,
                     cookies=self.cookies,
                     json=self.request_data)
        return get_detial_json.json()

if __name__ == "__main__":
    test = get_activity_information("https://hd.chaoxing.com/hd/activity/4109616",2302291,949506)
    print(test.get_info())
    print(test.connect_code,test.json)