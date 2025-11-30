import requests
# from urllib.parse import unquote
from color import colored_opt
from typing import overload
import json

class get:
    def __init__(self,*args) -> None:
        self.cookies = {}
        # self.headers = {}
        # self.request_data = ""
        self.connect_code = -1
        self.response_text = ""
        self.cookies = self.split_cookies(open("cookies.txt","r",encoding="utf8").read())
        self.c_mgr = colored_opt()
        if not args :
            self.headers,self.request_data = self.read_head_file(self.headers_path)

    def read_head_file(self,file_path)->dict:
        headers = {}
        request_data = []
        with open(file_path,'r') as headers_f:

            while True:
                header_option = headers_f.readline().strip()
                if not header_option : break
                k_v = self.split_lines(header_option)
                if k_v[0] == "data":
                    request_data = k_v[1]
                else:
                    headers[k_v[0]] = k_v[1]
        return (headers,request_data)
    def split_lines(self,line:str) -> tuple:
        index = line.find(":")
        assert index,'未找到":"'
        key = line[:index]
        value = line[index+2:]
        return (key,value)
    

    def split_cookies(self,cookies:str) -> dict:
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
    def get_info(self):

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
    def __init__(self, *args):
        self.headers_path = "activity_headers.txt"
        self.source_url = 'https://hd.chaoxing.com'
        self.backend_api = '/hd/api/activity/list/participate'
        super().__init__(*args)


    def get_activity_json(self) -> str:
        request_url = self.source_url + self.backend_api
        get_session = requests.session()
        

        chaoxing_response = get_session.post(request_url,headers=self.headers,data=self.request_data,cookies=self.cookies)
        self.connect_code = chaoxing_response.status_code
        self.response_text = chaoxing_response.text
        get_session.close()
        return self.response_text

    
class get_activity_information(get):
    def __init__(self, preview_url:str,pageId:int,websiteId:int,*args) -> None:
        self.headers_path = "activity_information_headers.txt"
        self.source_url = "https://api.hd.chaoxing.com"
        self.backend_api = "/mh/v3/activity/info"
        self.preview_url = preview_url
        self.pageId = pageId
        self.websiteId = websiteId
        self.pre_request_headers = self.read_head_file("domain_activity_information_headers.txt")[0]
        
        super().__init__(*args)
        
        self.sub_domain = self.get_domain()
        self.request_data = json.loads(self.request_data)
        self.request_data["pageId"] = pageId
        self.request_data["websiteId"] = websiteId

        tmp = self.headers["Origin"][:8] + self.sub_domain + self.headers["Origin"][16:]
        self.headers["Origin"] = tmp
        self.headers["Referer"] = tmp + "/"
        self.json = self.get_json()
    def get_domain(self) -> None:
        session = requests.session()
        request = session.get(self.preview_url,
                    headers=self.pre_request_headers,
                    cookies=self.cookies,
                    allow_redirects=False,
                    timeout=(3,5))
        # print(request)
        return request.headers.get('Location')[8:16]
    def get_json(self):
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