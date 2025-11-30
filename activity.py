from typing import Dict,Any,Tuple,overload
import time
import datetime
import json

from get_activity import get_activity_information
from color import colored_opt

class activity_constructer:
    @overload
    def __init__(self,raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,raw_json:Dict[str,Any],second_raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,*args) -> None:...

    def __init__(self,*args) -> None:
        raw_json:Dict[str, Any] = {}
        second_raw_json = {}
        if len(args) == 0:
            # TODO:构造一个example
            pass
        elif len(args) == 1:
            raw_json = args[0]
            second_raw_json = get_activity_information(raw_json["previewUrl"],raw_json["pageId"],raw_json["websiteId"]).json["data"]["results"]


        elif len(args) == 2:
            raw_json = args[0]
            second_raw_json = args[1]["data"]["results"]
        else:
            raise "Invalid arguement: Too namy arguements"
        
                

        
        self.name = raw_json["name"]
        self.start_time,self.end_time = self.format_date(second_raw_json[2]["fields"][2]["value"])
        self.class_start_time = raw_json["startTime"] / 1000
        self.class_end_time = raw_json["endTime"] / 1000
        self.name = raw_json["name"]
        # self.status = {"未开始":0,"报名中":1,"即将开始":2,"进行中":3,"已结束":4}[raw_json["signUpStatusDescribe"]]
        self.address = raw_json["detailAddress"] or "线上"
        self.maxium_people = raw_json["personLimit"]
        self.current_people = raw_json["signedUpNum"]
        self.c_mgr = colored_opt()
        self.belong_group = ["信息工程学院","8号楼","线上"]
        self.organisers = raw_json["organisers"]

        self.friendly_class_name = self.name
        self.friendly_address_name = self.address
        if len(self.friendly_class_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9] + self.c_mgr.default + self.c_mgr.yellow + "..." + self.c_mgr.default
        if len(self.friendly_address_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9] + self.c_mgr.default + self.c_mgr.yellow + "..." + self.c_mgr.default

    #格式化日期
    # 可能1："11月28日 15:51 ~ 12月1日 10:00"
    # 可能2："11月28日（周五） 15:51 ~ 18:00"
    # 可能3："11月28日 15:51 ~ 18:00"
    # 可能4："2025年11月27日周四 09:00"
    def format_date(self,date_range: str) -> Tuple[int, int]:
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
    def is_ready(self) -> dict:
        status_dict = self.get_status()
        
        return not (status_dict["time"] == "closed" or status_dict["reg"] == "full" or not status_dict["belong"]) # 未开始报名也返回true

    # 输出格式化简报
    def get_status(self) -> dict:
        status_dict = {"time":"great_chance", # 已结束(closed)，未开始(not_started),可以报名(great_chance)
                "belong":False, # 是否符合报名资格
                "reg":"", # 人数已满(full)，人数没有过半(free)，人数过半(busy)，没有上限(infinite)
                } 

        if time.time() > self.end_time:                         status_dict["time"] = "closed"
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


if __name__ == "__main__":
    test = activity_constructer(json.load(open("dier.json",'r',encoding='utf8'))['data']['records'][0],json.load(open("dier2.json",'r',encoding='utf8')))
    print(test.start_time,test.end_time)
    