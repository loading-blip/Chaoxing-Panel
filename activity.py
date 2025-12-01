from typing import Dict,Any,Tuple,overload
import time
import datetime
import json
import os

from get_activity import get_activity_describe,get_activity_detial,get_302_Location,get_activity_HTML
from u033_tools import colored_opt

class activity_constructer:
    """
    第二课堂活动类，将json数据处理，提供当前课程报名状态
    """

    @overload
    def __init__(self,raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any]) -> None:...


    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any]={}) -> None:
        """
        不传入值则会创建一个Example，只传入raw_json会自动获取second_raw_json
        Args:
            raw_json(Dict[str,Any], optional): 爬取到的单个课程json
            second_raw_json(Dict[str,Any], optional): 爬取到的此课程描述
        """
        self.sub_domain = get_302_Location(raw_json["id"]).domain
        if not second_raw_json:
            self.activity_detial = get_activity_detial(raw_json["pageId"],raw_json["websiteId"],self.sub_domain)
            second_raw_json = self.activity_detial.json["data"]["results"]
        else:
            second_raw_json = second_raw_json["data"]["results"]
        
        self.name = raw_json["name"]
        self.start_time,self.end_time = self.format_date(self.get_time_in_json(second_raw_json))
        self.class_start_time = raw_json["startTime"] / 1000
        self.class_end_time = raw_json["endTime"] / 1000
        self.name = raw_json["name"]
        self.id = raw_json["id"]
        # self.status = {"未开始":0,"报名中":1,"即将开始":2,"进行中":3,"已结束":4}[raw_json["signUpStatusDescribe"]]
        self.address = raw_json["detailAddress"] or "线上"
        self.maxium_people = raw_json["personLimit"]
        self.current_people = raw_json["signedUpNum"]
        self.c_mgr = colored_opt()
        self.belong_group = ["信息工程学院","8号楼","线上"]
        self.organisers = raw_json["organisers"]

        self.wfwfid = get_activity_HTML(self.sub_domain,raw_json["pageId"])
        self.activity_describe = get_activity_describe(raw_json["pageId"],raw_json["websiteId"],self.wfwfid)
        self.describe = self.activity_describe.describe
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
                } 
        if not self.start_time:                                   status_dict["time"] = "great_chance"  #没有时间默认可抢
        elif time.time() > self.end_time:                         status_dict["time"] = "closed"
        elif time.time() < self.start_time:                       status_dict["time"] = "not_started"

        for i in self.belong_group:
            if i in self.organisers: 
                status_dict["belong"] = True
                break
        
        if not self.maxium_people:                              status_dict["reg"] = "infinite"
        elif self.maxium_people == self.current_people:         status_dict["reg"] = "full"
        elif self.current_people / self.maxium_people <= 0.5:   status_dict["reg"] = "busy"
        else:                                                   status_dict["reg"] = "free"
        return status_dict
    def generate_HTML(self,document:str,path="tmp/") -> None:
        def sanitize_filename_translate(filename):
            """使用str.translate移除不安全字符"""
            # 定义需要过滤的字符
            unsafe_chars = '<>:"/\\|?*'  # Windows/Linux常见非法字符
            # 创建翻译表：将不安全字符映射为None（即删除）
            translator = str.maketrans('', '', unsafe_chars)
            return filename.translate(translator)
        with open(os.path.join("tmp",sanitize_filename_translate(f"{self.id}.html")),"w",encoding="utf8") as html_file:
            html_file.write(document)
        


if __name__ == "__main__":
    test = activity_constructer(json.load(open("dier.json",'r',encoding='utf8'))['data']['records'][0],json.load(open("dier2.json",'r',encoding='utf8')))
    print(test.start_time,test.end_time)
    