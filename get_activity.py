import requests
# from urllib.parse import unquote
from color import colored_opt

class get_activity:
    def __init__(self) -> None:...
    
    def __init__(self,request_attr) ->None:...
    
    def __init__(self,*args) -> None:
        self.headers = {}
        self.request_data = ""
        self.source_url = 'https://hd.chaoxing.com'
        self.backend_api = '/hd/api/activity/list/participate'
        self.connect_code = -1
        self.response_text = ""
        if not args :
            with open("headers.txt",'r') as headers:
                while True:
                    header_option = headers.readline().strip()
                    if not header_option : break
                    k_v = self.split_lines(header_option)
                    if k_v[0] == "data":
                        self.request_data = k_v[1]
                    else:  
                        self.headers[k_v[0]] = k_v[1]
        # if args == 1:
            
    def split_lines(self,line:str) -> tuple:
        index = line.find(":")
        assert index,'未找到":"'
        key = line[:index]
        value = line[index+2:]
        return (key,value)
    def get_activity_json(self) -> str:
        request_url = self.source_url + self.backend_api
        get_session = requests.session()
        

        chaoxing_response = get_session.post(request_url,headers=self.headers,data=self.request_data)
        self.connect_code = chaoxing_response.status_code
        self.response_text = chaoxing_response.text
        get_session.close()
        return self.response_text
    def get_info(self):
        c_opt = colored_opt()

        request_url = self.source_url + self.backend_api
        requests_head = []
        requests_data = self.request_data
        
        for k,v in self.headers.items():
            if len(v)>50:
                v = v[:48]+"..."
            requests_head.append(f"{c_opt.blue}{k}{c_opt.default}: {v}") 
        


        opt =[f"{c_opt.purple}url{c_opt.default}: {request_url}",
              f"{c_opt.purple}headers{c_opt.default}: \n\t{"\n\t".join(requests_head)}",
              f"{c_opt.purple}data{c_opt.default}: {requests_data}"]

        return "\n".join(opt)
if __name__ == "__main__":
    test = get_activity()
    print(test.get_info())
    test.get_activity_json()
    print(test.connect_code,test.response_text)