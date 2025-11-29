import json
import time
import logging
import sys

from activity import activity_constructer
from get_activity import get_activity

# TODO:使用req动态获取第二课堂JSON
def get_activity_list_json()-> dict: 
    activity_raw = get_activity().get_activity_json()
    return json.loads(activity_raw)

activity_json = get_activity_list_json()

if activity_json['code']!= 1 : 
    logging.error("返回结果有误")
    sys.exit(1)

activity_list = [activity_constructer(i) for i in activity_json['data']['records']]


for i in activity_list:
    # if i.is_ready():
        print(i.print_status())
    
