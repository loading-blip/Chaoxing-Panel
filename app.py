import json
import time
import logging
import sys
from tqdm import tqdm

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

process_bar = tqdm(total=10)
activity_list = []
# 防止请求超限
for i in activity_json['data']['records']:
    activity_list.append(activity_constructer(i))
    process_bar.update(1)
    time.sleep(1)
process_bar.close()

opt_list = []

for activity in activity_list:
    #TODO:正在制作过滤已结束输出的选项
    status = activity.get_status()
    color = ""
    # 金色为人数过半，绿色为人数空闲或无上限，蓝色为未开始，灰色为过期或无资格
    # 此处为包含所有可报名的可能
    if status["time"] == "closed" or not status["belong"]:  color = c_mgr.half_light
    # elif status["time"] == "not_started":                   color = c_mgr.blue
    elif status["reg"] == "full":                           color = c_mgr.red
    elif status["reg"] == "busy":                           color = c_mgr.yellow 
    else: color = c_mgr.green 
    
    # print(status)
    # HACK:更换为可阅读的代码，其实以下那坨是用来调试的（
    opt_list.append(f"{color}{activity.friendly_class_name:<10}{c_mgr.default}\t{c_mgr.light_blue}人数{c_mgr.default}:{activity.current_people}/{activity.maxium_people if activity.maxium_people else "∞"}\t{c_mgr.light_blue}位置{c_mgr.default}:{activity.friendly_address_name:<10}\t{c_mgr.light_blue}报名时间{c_mgr.default}:{time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.start_time))} - {time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.end_time))}\t{c_mgr.light_blue}上课时间{c_mgr.default}:{time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_start_time))} - {time.strftime("%Y-%m-%d %H:%M", time.localtime(activity.class_end_time))}")

print("\n".join(opt_list))