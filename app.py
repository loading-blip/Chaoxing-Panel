import json
import time
import logging
import sys
import os
import threading
from tqdm import tqdm
from typing import List,Dict
from tabulate import tabulate
from html.parser import HTMLParser
from flask import Flask,make_response,request,jsonify

from activity import activity_constructer
from get_activity import get_activity
from u033_tools import colored_opt,Terminal_support

class backend_web:
    """后端服务器类"""
    def __init__(self) -> None:
        self.app = Flask(__name__)
        self._register_routes()

    def cors_headers(self,response) ->dict:
        response.headers['Access-Control-Allow-Origin'] = "*"
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        response.headers['Access-Control-Allow-Methods'] = 'GET, OPTIONS'
        return response
    
    def _register_routes(self) -> None:
        @self.app.after_request
        def after_request(response:dict)->dict:
            """在每个请求后自动添加 CORS 头部"""
            return self.cors_headers(response)


        @self.app.route('/')
        def home():
            return "Hello?"


        @self.app.route('/status')
        def ret_status():
            if shared_data.get_status() == "Done":
                status = {"status":"complete",
                          "complete":True}
            else:
                status = {"status":"working",
                          "current_work":shared_data.get_current_work(),
                          "current_quantity":shared_data.get_current_quantity(),
                          "quantity":shared_data.get_quantity(),
                          "complete":False}
            return jsonify(json.dumps(status))

        @self.app.route('/data', methods=['GET', 'OPTIONS'])
        def data():
            if request.method == "OPTIONS":
                headers =  self.cors_headers(make_response())
                return headers
            activity_list = shared_data.get_data_json()
            response = {"code":"200","data":activity_list}
            return jsonify(json.dumps(response))
        
    def run_app(self):
        self.app.run(port=5000,debug=True)

class HTMLTextExtractor(HTMLParser):
    """HTML标签移除器"""
    def __init__(self):
        super().__init__()
        self.result = []
    
    def handle_data(self, data):
        self.result.append(data)
    
    def get_text(self):
        return ''.join(self.result)

class chaoxing_activity:
    """第二课堂数据获取类"""
    def __init__(self):
        self.raw_data =[]
        self.data:List[Dict[str,str]] = []
        
    def run_request(self):
        self.raw_data = self.get_data()
        self.data = self.format_data(self.raw_data)

        print(self)

        shared_data.set_current_work(f'完成!')
        shared_data.set_status("Done")
        shared_data.set_data_json(self.data)

    # requests动态获取第二课堂JSON
    def _get_activity_list_json(self)-> dict: 
        activity_raw = get_activity().get_activity_json()
        return json.loads(activity_raw)
    # return json.load(open("dier.json",'r',encoding='utf8'))
    def get_data(self):
        shared_data.set_current_work("正在获取第二课堂列表中...")
        activity_json = self._get_activity_list_json()
        if activity_json['code']!= 1 : 
            logging.error("返回结果有误")
            sys.exit(1)

        if not os.path.exists("tmp"):
            os.mkdir("tmp")

        process_bar = tqdm(total=len(activity_json['data']['records']))
        activity_list:List[activity_constructer] = []

        for activity in activity_json['data']['records']:
            shared_data.set_current_work(f'正在获取"{activity["name"]}"的详细信息...')
            shared_data.acc_current_quantity()
            activity_list.append(activity_constructer(activity))
            process_bar.update(1)
            # time.sleep(1)
        process_bar.close()
        return activity_list
    def format_data(self,raw_data:List[activity_constructer]) -> List[Dict[str,str]]:
        activities = []
        # HACK: 代码重复，下次重构解决
        for activity in raw_data:
            shared_data.set_current_work(f'正在处理"{activity.name}"的详细信息...')
            
            html = HTMLTextExtractor()
            html.feed(activity.describe)
            start_time = "无" if not activity.start_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.start_time))
            end_time = "无" if not activity.end_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.end_time))
            class_start_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_start_time))
            class_end_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_end_time))
            describe = html.get_text() if len(html.get_text()) < 15 else html.get_text()[:12]+"..."

            activity_dict = {
            "名称":activity.name,
            "人数":f"{activity.current_people if activity.current_people else "∞"}/{activity.maxium_people if activity.maxium_people else "∞"}",
            "位置":activity.address,
            "报名开始时间":start_time,
            "报名结束时间":end_time,
            "活动开始时间":class_start_time,
            "活动结束时间":class_end_time,
            "描述":describe,
            }
            activities.append(activity_dict)
        return activities
    def __str__(self):
        # HACK: 代码重复，下次重构解决
        current_path = os.getcwd()
        c_mgr = colored_opt()

        opt_list = [[f"{c_mgr.light_blue}名称{c_mgr.default}",
                    f"{c_mgr.light_blue}人数{c_mgr.default}",
                    f"{c_mgr.light_blue}位置{c_mgr.default}",
                    f"{c_mgr.light_blue}报名开始时间{c_mgr.default}",
                    f"{c_mgr.light_blue}报名结束时间{c_mgr.default}",
                    f"{c_mgr.light_blue}活动开始时间{c_mgr.default}",
                    f"{c_mgr.light_blue}活动结束时间{c_mgr.default}",
                    f"{c_mgr.light_blue}描述{c_mgr.default}"
                    ],
                    ]

        for activity in self.raw_data:
            #TODO:正在制作过滤已结束输出的选项
            status = activity.get_status()
            color = ""
            # 金色为人数过半，绿色为人数空闲或无上限，蓝色为未开始，灰色为过期或无资格
            # 此处为包含所有可报名的可能
            if status["time"] == "closed" or not status["belong"]:  color = c_mgr.half_light
            elif status["time"] == "not_started":                   color = c_mgr.blue
            elif status["reg"] == "full":                           color = c_mgr.red
            elif status["reg"] == "busy":                           color = c_mgr.yellow 
            else:                                                   color = c_mgr.green 
            
            html = HTMLTextExtractor()
            html.feed(activity.describe)

            describe = html.get_text() if len(html.get_text()) < 15 else html.get_text()[:12]+"..."


            start_time = "无" if not activity.start_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.start_time))
            end_time = "无" if not activity.end_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.end_time))
            class_start_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_start_time))
            class_end_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_end_time))
            
            opt_list.append([color+activity.friendly_class_name+c_mgr.default,
                            f"{activity.current_people if activity.current_people else "∞"}/{activity.maxium_people if activity.maxium_people else "∞"}",
                            activity.friendly_address_name,
                            start_time,
                            end_time,
                            class_start_time,
                            class_end_time,
                            Terminal_support().println_link("file://"+os.path.join(current_path,"tmp",f"{activity.id}.html").replace('\\', '/'),describe)
                            ])

        table = tabulate(opt_list, headers="firstrow", tablefmt="grid")

        return table

class sharedData:
    """线程数据共享类"""
    def __init__(self) -> None:
        self.status = "not_yet"
        self.current_work = "initialization..."
        self.current_quantity = 0
        self.quantity = 10
        self.data_json:List[Dict[str,str]] = []
        self.lock = threading.Lock()
    def get_status(self):
        with self.lock:
            return self.status
    
    def get_current_work(self):
        with self.lock:
            return self.current_work
    
    def get_data_json(self):
        with self.lock:
            return self.data_json
        
    def set_status(self,value):
        with self.lock:
            self.status = value
    
    def set_current_work(self,value):
        with self.lock:
            self.current_work = value
    
    def set_data_json(self,value:List[Dict[str,str]]):
        with self.lock:
            self.data_json = value
    def get_current_quantity(self):
        with self.lock:
            return self.current_quantity
    def get_quantity(self):
        with self.lock:
            return self.quantity
    def set_current_quantity(self,value):
        with self.lock:
            self.set_current_quantity = value
    def set_quantity(self,value):
        with self.lock:
            self.quantity = value
    def acc_current_quantity(self):
        with self.lock:
            self.current_quantity += 1
shared_data = sharedData()

if __name__ == "__main__":
    running_code = 1
    
    activity_exam = chaoxing_activity()
    if running_code:
        backend_exam = backend_web()
        data_threading = threading.Thread(target=activity_exam.run_request)
        web_threading = threading.Thread(target=backend_exam.run_app)

        # web_threading.start()
        data_threading.start()
        # TIPS:flask需要为主线程才能debug
        web_threading.run()
    else:
        activity_exam.run_request()
        print(activity_exam)

