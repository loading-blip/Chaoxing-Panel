import json
import time
import logging
import sys
from tqdm import tqdm
from typing import List
from tabulate import tabulate

from activity import activity_constructer
from get_activity import get_activity
from color import colored_opt

c_mgr = colored_opt()

# requests动态获取第二课堂JSON
def get_activity_list_json()-> dict: 
    activity_raw = get_activity().get_activity_json()
    return json.loads(activity_raw)
    # return json.load(open("dier.json",'r',encoding='utf8'))

activity_json = get_activity_list_json()

if activity_json['code']!= 1 : 
    logging.error("返回结果有误")
    sys.exit(1)

process_bar = tqdm(total=len(activity_json['data']['records']))
activity_list:List[activity_constructer] = []

# 防止一段时间内请求超限
for activity in activity_json['data']['records']:
    activity_list.append(activity_constructer(activity))
    process_bar.update(1)
    time.sleep(1)
process_bar.close()

opt_list = [[f"{c_mgr.light_blue}名称{c_mgr.default}",
            f"{c_mgr.light_blue}人数{c_mgr.default}",
            f"{c_mgr.light_blue}位置{c_mgr.default}",
            f"{c_mgr.light_blue}报名开始时间{c_mgr.default}",
            f"{c_mgr.light_blue}报名开始时间{c_mgr.default}",
            f"{c_mgr.light_blue}活动开始时间{c_mgr.default}",
            f"{c_mgr.light_blue}活动结束时间{c_mgr.default}"
            ],
            ]

for activity in activity_list:
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
                    class_end_time
                    ])

table = tabulate(opt_list, headers="firstrow", tablefmt="grid")

print(table)