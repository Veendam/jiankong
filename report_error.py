# -*- coding: utf-8 -*-
#!/usr/bin/env python

import json
import requests


def report_error(info, phone=15115683713):
    url = "https://oapi.dingtalk.com/robot/send?access_token=fc9a0fd73290fb877c0d6f98e56fef5414803a1144e43b423f0ca4c85c55d320"
    msg = u"%s 报表发送出错!" % info
    headers = {"Content-Type": "application/json"}
    data = {'msgtype':'text',
        'text':{'content': msg},
        "at": {"atMobiles":[phone], "isAtAll": False}
         }
    r = requests.post(url, data=json.dumps(data), headers=headers)
    return r
    
 
if __name__ == "__main__":
    report_error(u'测试')
