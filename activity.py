from typing import Dict,Any,Tuple,overload
import time
import datetime
import json
import os
import logging
import sys
from tqdm import tqdm
from typing import List,Dict
from tabulate import tabulate
import threading

from html.parser import HTMLParser
from get_activity import *
from u033_tools import Colorful,Terminal_support
from config import Config

###########################
#   此文件内存放超星功能体
#   若需要新增功能
#   可以在这新建类
############################

class SharedData:
    """线程数据共享类"""
    def __init__(self) -> None:
        self.status = "not_yet"
        self.current_work = "initialization..."
        self.current_quantity = 0
        self.quantity = 10
        self.data_json = []
        self.session = ""
        self.lock = threading.Lock()
    
    def reload(self):
        self.status = "not_yet"
        self.current_work = "initialization..."
        self.current_quantity = 0
        self.quantity = 10
        self.session = ""
        self.data_json = []

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
    
    def set_session(self,value):
        with self.lock:
            self.session = value

    def get_session(self):
        with self.lock:
            return self.session
    def set_data_json(self,value):
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

class HTMLTextExtractor(HTMLParser):
    """HTML标签移除器"""
    def __init__(self):
        super().__init__()
        self.result = []
    
    def handle_data(self, data):
        self.result.append(data)
    
    def get_text(self):
        return ''.join(self.result)

class Activity:
    """
    第二课堂活动列表，将json数据处理，提供当前课程报名状态
    """

    @overload
    def __init__(self,raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,raw_json:Dict[str,Any],*,config:Config) -> None:...

    @overload
    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any],*,config:Config) -> None:...

    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any]={},config:Config=Config()) -> None:
        """
        不传入值则会创建一个Example，只传入raw_json会自动获取second_raw_json
        Args:
            raw_json(Dict[str,Any], optional): 爬取到的单个课程json
            second_raw_json(Dict[str,Any], optional): 爬取到的此课程描述
        """
        self.sub_domain = Get_activity_sub_domain(raw_json["id"]).domain
        if not second_raw_json:
            self.activity_detial = Get_activity_detial(raw_json["pageId"],raw_json["websiteId"],self.sub_domain)
            second_raw_json = self.activity_detial.json["data"]["results"]
        else:
            second_raw_json = second_raw_json["data"]["results"]
        
        self._config = config
        self.name = raw_json["name"]
        self.start_time,self.end_time = self.format_date(self.get_time_in_json(second_raw_json))
        self.class_start_time = raw_json["startTime"] / 1000
        self.class_end_time = raw_json["endTime"] / 1000
        self.id = raw_json["id"]
        self.is_registered = False
        self.is_register_link = ""
        self.address = raw_json["detailAddress"] or "线上"
        self.maxium_people = raw_json["personLimit"]
        self.current_people = raw_json["signedUpNum"]
        self.c_mgr = Colorful()
        self.belong_group = ["信息工程学院","8号楼","线上"]
        self.organisers = raw_json["organisers"]

        # self.wfwfid = Get_activity_HTML(self.sub_domain,raw_json["pageId"])
        self.Activity_describe = Get_activity_describe(raw_json["pageId"],raw_json["websiteId"],self.sub_domain)
        self.activity_btn_name = Get_activity_btn_name(raw_json["pageId"],raw_json["websiteId"],self.sub_domain)
    
        self.describe = self.Activity_describe.describe
        self.btn_name = self.activity_btn_name.btn_name
        self.friendly_class_name = self.name
        self.friendly_address_name = self.address
        if len(self.friendly_class_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9] + self.c_mgr.default + self.c_mgr.yellow + "..." + self.c_mgr.default
        if len(self.friendly_address_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9] + self.c_mgr.default + self.c_mgr.yellow + "..." + self.c_mgr.default
        self.generate_HTML(self.describe)


    def get_time_in_json(self,raw_json) -> str:
        """
        寻找每行描述中报名时间的一行并返回原始字符串，没有则返回"Null"
        Returns:
            str: raw time string or `Null`
        """
        for row in raw_json:
            if row["fields"][1]["value"] == "报名时间":     
                return row["fields"][2]["value"]
        return "Null"
    #格式化日期
    def format_date(self,date_range: str) -> Tuple[int, int]:
        """
        格式化非规范化日期字符串\n
        示例1：`11月28日 15:51 ~ 12月1日 10:00`\n
        示例2：`11月28日（周五） 15:51 ~ 18:00`\n
        示例3：`11月28日 15:51 ~ 18:00`\n
        示例4：`2025年11月27日周四 09:00`\n
        Args:
            date_range(str): 包含"月","日"关键字的日期字符串
        Returns:
            tuple(int,int): 返回报名区间时间戳
        """
        if date_range == "Null":
            return (0,0)
        def format_step(raw_time:str,refer_time:datetime.datetime = datetime.datetime.now()) -> datetime.datetime:

            year_index = raw_time.find("年")
            month_index = raw_time.find("月")
            day_index = raw_time.find("日")
            # 海象运算符来着，不然要多写两行
            time_index = l if (l:=raw_time.find(":"))>(r:=raw_time.find("：")) else r
            
            if year_index != -1:
                refer_time = refer_time.replace(year = int(raw_time[:year_index]),
                                month = int(raw_time[year_index+1:month_index]),
                                day = int(raw_time[month_index+1:day_index])
                                )
            elif month_index != -1:
                refer_time = refer_time.replace(month = int(raw_time[:month_index]),
                                    day = int(raw_time[month_index+1:day_index])
                                    )
            elif day_index !=-1:
                refer_time = refer_time.replace(day = int(raw_time[:day_index]))
            
            if time_index == -1:
                refer_time = refer_time.replace(hour=0,minute=0,second=0,microsecond=0)
            else:
                refer_time = refer_time.replace(hour=int(raw_time[time_index-2:time_index]),
                                minute=int(raw_time[time_index+1:time_index+3]),
                                second=0,
                                microsecond=0)
            return refer_time
        date_interval = date_range.replace(" ","").split("~")
        start_time = format_step(date_interval[0])
        end_time = format_step(date_interval[1],start_time)
        return (int(start_time.timestamp()),
                int(end_time.timestamp()))


    # TODO:判断当前是否可以报名
    def is_ready(self) -> bool:
        """
        返回你是否可以报名，注意：未开始报名也返回true
        Returns:
            bool:
                - True: 你有资格签到
                - False: 你没资格了 
        """
        status_dict = self.get_status()
        
        return not (status_dict["time"] == "closed" or status_dict["reg"] == "full" or not status_dict["belong"]) # 未开始报名也返回true

    # 输出格式化简报
    def get_status(self) -> dict:
        """
        返回一个状态字典
        Returns:
            dict: 状态字典
            - time(str): 用户ID
            - belong(bool): 是否在参加范围内
            - reg(str): 人数状态
        """
        status_dict = {"time":"great_chance", # 已结束(closed)，未开始(not_started),可以报名(great_chance)
                "belong":False, # 是否符合报名资格
                "reg":"", # 人数已满(full)，人数没有过半(free)，人数过半(busy)，没有上限(infinite)
                "state":False # 当前账号报名此活动的状态
                } 
        if  (self.btn_name in self._config.btn_can_reg_names) or not self.start_time:
            status_dict["time"] = "great_chance"  #没有时间默认可抢
        elif (self.btn_name in self._config.btn_cannot_reg_names) or (time.time() > self.end_time):
            status_dict["time"] = "closed"
        elif time.time() < self.start_time:
            status_dict["time"] = "not_started"

        # 检测是否在参与范围内
        if self.btn_name in self._config.btn_cannot_reg_names:
            status_dict["belong"] = True
        else:
            for i in self.belong_group:
                if i in self.organisers: 
                    status_dict["belong"] = True
                    break
        
        if self.btn_name in self._config.btn_reg_names:
            status_dict['state'] = True

        if not self.maxium_people:                              status_dict["reg"] = "infinite"
        elif self.maxium_people == self.current_people:         status_dict["reg"] = "full"
        elif self.current_people / self.maxium_people <= 0.5:   status_dict["reg"] = "busy"
        else:                                                   status_dict["reg"] = "free"
        return status_dict
    def generate_HTML(self,document:str) -> None:
        raw_head = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Document</title>
                        <link rel="stylesheet" href="../css.css">
                    </head>
                    <body>
                    """
        raw_tail = """</body>
                    </html>"""
        def sanitize_filename_translate(filename):
            """使用str.translate移除不安全字符"""
            # 定义需要过滤的字符
            unsafe_chars = '<>:"/\\|?*'  # Windows/Linux常见非法字符
            # 创建翻译表：将不安全字符映射为None（即删除）
            translator = str.maketrans('', '', unsafe_chars)
            return filename.translate(translator)
        with open(os.path.join("tmp",sanitize_filename_translate(f"{self.id}.html")),"w",encoding="utf8") as html_file:
            html_file.write(raw_head)
            html_file.write(document)
            html_file.write(raw_tail)
        
class Chaoxing_activity:
    """第二课堂数据获取类"""
    def __init__(self,shared_data,config:Config):
        self.raw_data =[]
        self.data:List[Dict[str,str]] = []
        self.shared_data = shared_data
        self._config = config

    def run_request(self):
        self.raw_data = self.get_data()
        self.data = self.format_data(self.raw_data)

        print(self)

        self.shared_data.set_current_work(f'完成!')
        self.shared_data.set_status("Done")
        self.shared_data.set_data_json(self.data)

    # requests动态获取第二课堂JSON
    def _Get_Activity_list_json(self)-> dict: 
        activity_raw = Get_activity().Get_activity_json()
        return json.loads(activity_raw)
    # return json.load(open("dier.json",'r',encoding='utf8'))
    def get_data(self):
        self.shared_data.set_current_work("正在获取第二课堂列表中...")
        activity_json = self._Get_Activity_list_json()
        if activity_json['code']!= 1 : 
            logging.error("返回结果有误")
            sys.exit(1)

        if not os.path.exists("tmp"):
            os.mkdir("tmp")

        process_bar = tqdm(total=len(activity_json['data']['records']))
        Activity_list:List[Activity] = []

        for activity in activity_json['data']['records']:
            self.shared_data.set_current_work(f'正在获取"{activity["name"]}"的详细信息...')
            self.shared_data.acc_current_quantity()
            Activity_list.append(Activity(activity,config=self._config))
            process_bar.update(1)
            # time.sleep(1)
        process_bar.close()
        return Activity_list
    def format_data(self,raw_data:List[Activity]) -> List[Dict[str,str]]:
        activities = []
        # HACK: 代码重复，下次重构解决
        for activity in raw_data:
            self.shared_data.set_current_work(f'正在处理"{activity.name}"的详细信息...')
            
            html = HTMLTextExtractor()
            html.feed(activity.describe)
            start_time = "无" if not activity.start_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.start_time))
            end_time = "无" if not activity.end_time else time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.end_time))
            class_start_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_start_time))
            class_end_time = time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_end_time))
            describe = html.get_text() if len(html.get_text()) < 15 else html.get_text()[:12]+"..."

            status = activity.get_status()
            report = ""
            # 金色为人数过半，绿色为人数空闲或无上限，蓝色为未开始，灰色为过期或无资格
            # 此处为包含所有可报名的可能
            if status["time"] == "closed" or not status["belong"]:  report = "unavailable"
            elif status["time"] == "not_started":                   report = "not_started"
            elif status["reg"] == "full":                           report = "full"
            elif status["state"]:                                   report = "regd"
            elif status["reg"] == "busy":                           report = "busy"
            else:                                                   report = "great_chance"

            activity_dict = {
            "名称":activity.name,
            "人数":f"{activity.current_people if activity.current_people else "∞"}/{activity.maxium_people if activity.maxium_people else "∞"}",
            "位置":activity.address,
            "报名开始时间":start_time,
            "报名结束时间":end_time,
            "活动开始时间":class_start_time,
            "活动结束时间":class_end_time,
            "描述":describe,
            "status": report,
            }
            activities.append(activity_dict)
        return activities
    def __str__(self):
        # HACK: 代码重复，下次重构解决
        current_path = os.getcwd()
        c_mgr = Colorful()

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

class Chaoxing_transcript:
    def __init__(self,shared_data:SharedData) -> None:
        self.real_name = ""
        self.max_score:float = 0.0
        self.act_type = []
        self.act_record = []
        self.shared_data = shared_data

        self._act_type:Get_activity_type
        self._act_record:Get_activity_record

    def run_request(self):
        self.shared_data.set_current_work("正在获取参与过的项目....")
        self.act_record = self.get_record()

        self.shared_data.set_current_work("正在获取学校积分类型....")
        self.act_type = self.get_type()

        self.shared_data.set_current_work(f'完成!')
        self.shared_data.set_status("Done")
        self.shared_data.set_data_json(self.get_pack())

    def get_record(self):
        self._act_record = Get_activity_record()
        self.real_name = self._act_record.json[0]['userName']
        return self._act_record.json
    
    def get_type(self):
        if not self.real_name:
            self.act_record = self.get_record()
        self._act_type = Get_activity_type(self.real_name)
        for type in self._act_type.json:
            self.max_score += type['minScore'] if type['minScore'] else 0.0
        return self._act_type.json

    def get_pack(self):
        return {
            "max_score": self.max_score,
            "realName": self.real_name,
            "type_data": self.act_type,
            "records": self.act_record
        }

if __name__ == "__main__":
    # test = Chaoxing_transcript(SharedData())
    test = Activity(json.load(open('test_resources/dier-1.json','r',encoding='utf8')),config=Config())
    print(test.get_status())
    print(test.btn_name)