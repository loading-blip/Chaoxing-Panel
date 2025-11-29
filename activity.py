from typing import Dict,Any,overload
import time
from color import colored_opt

class activity_constructer:
    @overload
    def __init__(self,raw_json:Dict[str,Any]) -> None:...

    @overload
    def __init__(self,*args) -> None:...

    def __init__(self,*args) -> None:
        if len(args) == 1 :
            assert isinstance(args[0], dict) ,"参数不正确"
            raw_json:Dict[str, Any] = args[0]
            self.name = raw_json["name"]
            self.start_time = raw_json["startTime"]
            self.end_time = raw_json["endTime"] / 1000
            self.name = raw_json["name"]
            self.status = {"未开始":0,"报名中":1,"即将开始":2,"进行中":3,"已结束":4}[raw_json["signUpStatusDescribe"]]
            self.address = raw_json["detailAddress"]
        else:
            self.name = args[0]
            self.start_time = args[1]
            self.end_time = args[2]
            self.name = args[3]
            self.status = args[4]
            self.address = args[5]
        self.is_forecast = time.time() < self.start_time

        self.friendly_class_name = self.name
        self.friendly_address_name = self.address
        if len(self.friendly_class_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9]+ "..."
        if len(self.friendly_address_name) >= 10:
            self.friendly_class_name = self.friendly_class_name[:9]+ "..."

    # TODO:判断是否符合报名资格
    def is_ready(self) -> int:
        """
            return:
                0:  No
                1:  Yes
                2:  Yes,forecast
        """
        if time.time() > self.end_time: return 0
        if self.status > 2 : return 0

        return 1 + self.is_forecast
    # TODO:输出格式化简报
    def print_status(self) -> str:
        c_mgr = colored_opt()
        opt = ""
        
        # 绿色为可抢，蓝色为未开始，灰色为过期
        opt += f"{[c_mgr.half_light,c_mgr.green,c_mgr.blue][self.is_ready()]}{self.friendly_class_name:<12}\t{c_mgr.default} ->"
        
        # 地址为紫色，截止时间为黄色
        opt += f"\t{c_mgr.purple}地址{c_mgr.default}：\t{self.friendly_address_name :<12}"

        opt += f"\t{c_mgr.yellow}截止时间{c_mgr.default}：\t{time.strftime(r"%m/%d %H:%M",time.localtime(self.end_time))}"
        return opt
          